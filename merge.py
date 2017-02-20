import pkg_resources
import sys

try:
    pkg_resources.get_distribution('Products.CMFPlone')
except pkg_resources.DistributionNotFound:
    print 'ERROR, use: ./bin/zopepy ./src/profile-merge-tool/merge.py'
    sys.exit(1)


from collections import defaultdict
from ftw.upgrade.directory.scaffold import UpgradeStepCreator
from lxml import etree
from operator import attrgetter
from operator import itemgetter
from operator import methodcaller
from path import Path
from plone.memoize import instance
from pprint import pprint
from StringIO import StringIO
import difflib
import os
import re


XML_CHILD_INDENT = 4
XML_ATTR_INDENT = 6
_marker = object()

# Tags to format on a single line
XML_FORMAT_ONELINE = (
    'object',
    'property',
    'index',
    'hidden',
    'order',
    'viewlet',
)

# Tags to format on multiple lines
XML_FORMAT_MULTILINE = (
    'layer',
    'configlet',
)


def step(message):
    def decorator(func):
        def wrapper(*args, **kwargs):
            return execute_step(message, func, *args, **kwargs)
        return wrapper
    return decorator


def xpath_one(doc, xpath, default=_marker):
    nodes = doc.xpath(xpath)
    if default == _marker:
        assert len(nodes) == 1, 'Found {} {!r}, expected 1'.format(
            len(nodes), xpath)
    elif len(nodes) == 0:
        return default
    return nodes[0]


def execute_step(message, func, *args, **kwargs):
    print '\xf0\x9f\x94\xa7 ', message
    try:
        returnvalue = func(*args, **kwargs)
    except:
        print '\xf0\x9f\x92\xa5'
        raise
    else:
        print '\xe2\x9c\x94 \xf0\x9f\x8d\xba'
        print ''
        return returnvalue


class MergeTool(object):

    def __init__(self):
        self.here_dir = Path(__file__).parent.abspath()
        self.buildout_dir = Path(__file__).parent.parent.parent.abspath()
        assert self.buildout_dir.joinpath('bootstrap.py'), \
            'Could not find buildout root.'
        self.opengever_dir = self.buildout_dir.joinpath('opengever')
        self.og_core_profile_dir = self.opengever_dir.joinpath(
            'core', 'profiles', 'default')

    def __call__(self):
        self.create_opengever_core_profile()
        self.list_old_profiles()
        self.embedd_profiles_into_upgrade_steps()
        self.migrate_dependencies()
        self.remove_examplecontent_dependency()
        self.declare_examplecontent_softdependency()
        self.validate_dependencies()
        self.migrate_standard_xmls()
        self.migrate_mailhost()
        self.migrate_actions()
        self.migrate_rolemap()
        self.migrate_workflows()
        self.migrate_types()
        self.cleanup_jsregistry()
        self.cleanup_viewlets()
        self.validate_no_leftovers()
        self.migrate_hook_registrations()
        self.install_the_new_profile()
        self.apply_patches()
        self.add_upgrade_step()
        self.keep_old_profiles()

    @step('Create opengever.core Generic Setup profile.')
    def create_opengever_core_profile(self):
        source = self.here_dir.joinpath('opengever-core')
        target = self.opengever_dir.joinpath('core')
        cmd = 'cp -r {}/* {}'.format(source, target)
        print '   >', cmd
        os.system(cmd)

    @step('These profiles will be merged in this order:')
    def list_old_profiles(self):
        for profile in self.profiles_to_migrate:
            print '  ', profile

    @step('Embedd opengever.* profiles into upgrade steps installing them.')
    def embedd_profiles_into_upgrade_steps(self):
        # At this time, there is no upgrade step installing an opengever.*
        # component in code, usually a metadata.xml is used.
        # Verify that this did not change.
        upgradesteps = filter(lambda path: path.name == 'upgrade.py',
                              self.opengever_dir.walkfiles())
        for path in upgradesteps:
            lines = path.bytes().splitlines()
            for line in filter(lambda line: 'setup_install_profile' in line, lines):
                profile = re.match(
                    '^ +self\.setup_install_profile\(\'profile-([^\']+)\'\)',
                    line).group(1)
                assert profile not in self.profiles_to_migrate, \
                    'Unexpectedly found an upgrade step installing {}'.format(
                        profile)

        # Find all metadata.xml's in upgrade steps.
        # When the upgade step is installing one of the profiles to migrate,
        # we need to copy everything to the upgrade step since we will empty
        # the profile later.
        for upgrade_dir in map(attrgetter('parent'), upgradesteps):
            dependencies = self.dependencies_in(upgrade_dir.joinpath('metadata.xml'))
            if len(dependencies) == 0:
                continue

            assert len(dependencies) == 1, \
                'Only one dependency supported in upgrade step metadata.xml' \
                ' at {}'.format(upgrade_dir)
            profile, = dependencies

            if profile not in self.profiles_to_migrate:
                continue

            profile_path = self.profile_path(profile)
            profile_metadata = profile_path.joinpath('metadata.xml')
            profile_dependencies = self.dependencies_in(profile_metadata)
            for dependency in profile_dependencies:
                assert dependency not in self.profiles_to_migrate, \
                    'Cannot copy profile recursively into upgrade step....'

            handled_by_patch = map(
                self.opengever_dir.joinpath,
                ('policy/base/upgrades/20160923114424_install_opengever_private',
                ))
            if upgrade_dir not in handled_by_patch:
                hooks_path = profile_path.parent.parent.joinpath('hooks.py')
                assert not hooks_path.isfile(), \
                    ('{} may get us in trouble because the code is no longer '
                     'in the upgrade step {}').format(hooks_path, upgrade_dir)

            # copy profile into ugprade step
            os.system('cp -r {}/* {}'.format(profile_path, upgrade_dir))

            # update metdata.xml
            if profile_dependencies:
                metadata_doc = parsexml(upgrade_dir.joinpath('metadata.xml'))
                map(metadata_doc.getroot().remove,
                    metadata_doc.getroot().getchildren())
                deps_node = etree.SubElement(metadata_doc.getroot(), 'dependencies')
                for dependency in profile_dependencies:
                    node = etree.SubElement(deps_node, 'dependency')
                    node.text = 'profile-' + dependency

                prettywrite(upgrade_dir.joinpath('metadata.xml'), metadata_doc)
            else:
                upgrade_dir.joinpath('metadata.xml').unlink()

    @step('Migrate GS dependencies into opengever.core profile.')
    def migrate_dependencies(self):
        # Migrate dependencies according to recursive dependency lookup,
        # skipping merged profiles.
        # We do not remove dependencies from old profiles since we will
        # no longer install them and we need the dependencies for upgrade
        # step ordering.
        target_metadata = self.og_core_profile_dir.joinpath('metadata.xml')
        with target_metadata.open() as fio:
            target_doc = etree.parse(fio)

        dependencies_node = target_doc.xpath('//dependencies')[0]

        # We do not need to reinstall Plone packages, therefore do not migrate
        # them.
        blacklist = (
            'plone.app.registry:default',
        )

        for profile in self.recursive_dependencies('opengever.policy.base:default'):
            if profile in self.profiles_to_migrate:
                # do not migrate dependency to migrated profiles (og.task, ..)
                continue
            if profile in blacklist:
                continue
            node = etree.SubElement(dependencies_node, 'dependency')
            node.text = 'profile-' + profile

        prettywrite(target_metadata, target_doc)

    @step('Remove examplecontent dependency to og.policy.base')
    def remove_examplecontent_dependency(self):
        for path in [
                self.opengever_dir.joinpath(
                    'examplecontent/profiles/default/metadata.xml'),
                self.opengever_dir.joinpath(
                    'policytemplates/policy_template/opengever.+package.name+/'
                    'opengever/+package.name+/profiles/default/metadata.xml')]:
            doc = parsexml(path)
            node, = doc.xpath(
                '//dependency[text()="profile-opengever.policy.base:default"]')
            node.getparent().remove(node)
            # mimetypes are installed explicitly in og.setup.
            node, = doc.xpath(
                '//dependency[text()="profile-opengever.policy.base:mimetype"]')
            node.getparent().remove(node)
            prettywrite(path, doc)

    @step('Declare examplecontent softdependency to og.core upgrade order')
    def declare_examplecontent_softdependency(self):
        for path in [
                self.opengever_dir.joinpath(
                    'examplecontent/upgrades/configure.zcml'),
                self.opengever_dir.joinpath(
                    'policytemplates/policy_template/opengever.+package.name+/'
                    'opengever/+package.name+/upgrades/configure.zcml.bob')]:
            doc = parsexml(path)
            node, = doc.xpath('//*[local-name()="directory"]')
            node.attrib['soft_dependencies'] = 'opengever.core:default'
            prettywrite(path, doc)

    @step('Validate dependencies to merged profiles in not merged profiles')
    def validate_dependencies(self):
        metadata_files = filter(
            lambda path: path.name == 'metadata.xml',
            self.opengever_dir.walkfiles())
        metadata_files = filter(
            lambda path: '/upgrades/' not in path,
            metadata_files)
        metadata_files = filter(
            lambda path: '/opengever.+package.name+/' not in path,
            metadata_files)
        invalid_target_profiles = self.profiles_to_migrate
        paths_to_invalid_profiles = map(self.profile_path, invalid_target_profiles)
        metadata_files = filter(
            lambda path: path.parent not in paths_to_invalid_profiles,
            metadata_files)

        for path in metadata_files:
            doc = parsexml(path)
            for node in doc.xpath('//dependency'):
                profile = re.sub('^profile-', '', node.text)
                assert profile not in invalid_target_profiles, \
                    'Dependency to {!r} should be removed from {}'.format(
                        profile, path)

    def migrate_standard_xmls(self):
        standard_xmls = (
            'browserlayer.xml',
            'catalog.xml',
            'controlpanel.xml',
            'cssregistry.xml',
            'jsregistry.xml',
            'portlets.xml',
            'properties.xml',
            'propertiestool.xml',
            'registry.xml',
            'repositorytool.xml',
            'skins.xml',
            'types.xml',
            'viewlets.xml',
            'workflows.xml',
            'portal_languages.xml',
        )

        map(lambda name: execute_step(
            'Migrating {}'.format(name), self.standard_migrate_xml, name),
            standard_xmls)

    @step('Migrate mailhost.xml')
    def migrate_mailhost(self):
        # There is only one mailhost.xml.
        # Since everything is in the XML roo tnode, we cannot use
        # standard_migrate_xml.
        xmls = self.find_file_in_profiles_to_migrate('mailhost.xml')
        assert len(xmls) == 1, 'Expected exactly 1 mailhost.xml, got {!r}'.format(
            xmls)
        xmls[0].move(self.og_core_profile_dir)

    @step('Migrate rolemap.xml')
    def migrate_rolemap(self):
        self.first_level_tag_xml_migration('rolemap.xml', ('roles', 'permissions'))

    @step('Migrate actions.xml')
    def migrate_actions(self):
        categories = (
            'document_actions',
            'site_actions',
            'folder_buttons',
            'object',
            'object_buttons',
            'portal_tabs',
            'user',
            'controlpanel',
            'jqueryui_panels',
            'mobile_buttons',
            'object_checkin_menu')

        self.first_level_tag_xml_migration(
            'actions.xml',
            map('object[@name="{}"]'.format, categories))

        path = self.opengever_dir.joinpath('core/profiles/default/actions.xml')
        doc = parsexml(path)

        # remove <property name="title"/> tags from actegories
        for node in doc.xpath('/object/object/property[@name="title"]'):
            node.getparent().remove(node)

        # normalize newlines between objects
        for node in doc.xpath('/object/object/object'):
            node.tail = '\n\n'

        prettywrite(path, doc)

    @step('Migrate workflows')
    def migrate_workflows(self):
        seen = []
        for path in reduce(list.__add__,
                           map(methodcaller('glob', '*/definition.xml'),
                               self.find_dir_in_profiles_to_migrate('workflows'))):
            wf_name = str(path.parent.name)
            if wf_name in seen:
                raise ValueError(
                    'Workflow definition for {!r} appears twice'.format(wf_name))
            seen.append(wf_name)

            target = self.og_core_profile_dir.joinpath(
                path.relpath(path.parent.parent.parent))
            target.parent.makedirs()
            path.move(target)
            path.parent.rmdir()
            path.parent.parent.rmdir_p()

    @step('Migrate types')
    def migrate_types(self):
        sources_by_filename = defaultdict(list)
        for path in reduce(list.__add__,
                           map(methodcaller('glob', '*.xml'),
                               self.find_dir_in_profiles_to_migrate('types'))):
            sources_by_filename[str(path.name)].append(path)


        # opengever.tasktemplates:default is installed BEFORE
        # opengever.meeting:default, but tasktemplates customizes
        # meetingdossier before it is even installed.
        # In order to fix such issues, we reorder some FTIs manually here:
        # move the primary XML to position 0
        for relpath in (
                'meeting/profiles/default/types/opengever.meeting.meetingdossier.xml',
                'policy/base/profiles/default/types/Plone_Site.xml',
        ):
            path = self.opengever_dir.joinpath(relpath)
            filename = str(path.name)
            sources_by_filename[filename].remove(path)
            sources_by_filename[filename].insert(0, path)


        target_types_dir = self.og_core_profile_dir.joinpath('types').mkdir()
        for filename, sources in sources_by_filename.items():
            sources = sources[:]  # copy
            target_path = target_types_dir.joinpath(filename)
            source_path = sources.pop(0)
            source_path.move(target_path)
            source_path.parent.rmdir_p()

            if not sources:
                continue

            with target_path.open('r') as fio:
                target_doc = etree.parse(fio)

            for source_path in sources:
                with source_path.open('r') as fio:
                    source_doc = etree.parse(fio)

                self.add_source_comment(target_doc.getroot(), source_path)
                for node in source_doc.getroot().getchildren():
                    if isinstance(node, etree._Comment) or \
                       node.tag == 'action':
                        target_doc.getroot().append(node)

                    elif node.tag == 'property' and \
                         node.attrib.get('name') == 'allowed_content_types':
                        if node.attrib.get('purge') not in ('False', 'false'):
                            raise ValueError(
                                'Error merging FTIs: '
                                'cannot merge <property> when not purging. '
                                'Attrs: {!r}'.format(node.attrib))
                        target_node = target_doc.xpath(
                            '//property[@name="allowed_content_types"]')
                        if len(target_node) != 1:
                            raise ValueError(
                                'Couldnt find 1 <property '
                                'name="allowed_content_types"> in {}'.format(
                                    target_path))

                        target_node, = target_node
                        map(target_node.append, node.getchildren())

                    else:
                        raise ValueError(
                            'Error merging FTIs: <{}> unsupported in {}.\n{!r}'
                            .format(node.tag, source_path,
                                    sources_by_filename[filename]))

                prettywrite(target_path, target_doc)
                source_path.unlink().parent.rmdir_p()

    @step('Cleanup jsregistry order')
    def cleanup_jsregistry(self):
        path = self.og_core_profile_dir.joinpath('jsregistry.xml')
        order = self.here_dir.joinpath('jsorder.txt').bytes().strip().splitlines()
        order_after = {order[i]: order[i-1] for i in range(1, len(order))}

        new_doc = parsexml(path)
        new = new_doc.getroot()
        map(new.remove, new.getchildren())

        old = parsexml(path)
        nodes = {node.attrib.get('id'): node for node in old.xpath('javascript')}
        for name in order:
            if name not in nodes:
                continue
            node = nodes[name]
            node.tail = '\n\n'
            node.attrib['insert-after'] = order_after[name]
            new.append(node)

        prettywrite(path, new_doc)

    @step('Cleanup viewlets.xml')
    def cleanup_viewlets(self):
        path = self.og_core_profile_dir.joinpath('viewlets.xml')
        doc = parsexml(path)

        # remove "migrated" comments since we are gonna reorder
        map(doc.getroot().remove,
            filter(lambda node: node.text.startswith('migrated'),
                   filter(lambda node: isinstance(node, etree._Comment),
                          doc.getroot().getchildren())))

        # merge <viewlet> into "same" <order> / <hidden> containers
        containers = {}
        for node in filter(lambda node: not isinstance(node, etree._Comment),
                                doc.getroot()):
            key = (node.tag, tuple(sorted(dict(node.attrib).items())))
            if key in containers:
                map(containers[key].append, node.getchildren())
                node.getparent().remove(node)
            else:
                containers[key] = node

        # now we may have duplicate <viewlet> tag per parent, lets clean up
        for container in filter(lambda node: not isinstance(node, etree._Comment),
                                doc.getroot()):
            viewlets = []
            for node in container.getchildren():
                key = (node.tag, tuple(sorted(dict(node.attrib).items())))
                if key in viewlets:
                    container.remove(node)
                else:
                    viewlets.append(key)

        prettywrite(path, doc)

    @step('Check for leftovers in old profiles')
    def validate_no_leftovers(self):
        errors = False

        for profile in self.profiles_to_migrate:
            for item in self.profile_path(profile).listdir():
                if item.name == 'metadata.xml':
                    continue
                if not errors:
                    print '   ERROR: leftovers found:'
                    errors = True

                print '  ', profile.ljust(35), item.isdir() and 'D' or ' ', item.name

        assert not errors, 'Should not have any leftovers'

    @step('Migrate hook registrations.')
    def migrate_hook_registrations(self):
        handler_by_profile = {}

        for path in self.opengever_dir.walkfiles('*.zcml'):
            with path.open() as fio:
                doc = etree.parse(fio)

            changes = False
            for node in doc.xpath('//*[local-name()="hook"]'):
                profile = node.attrib.get('profile')
                if profile not in self.profiles_to_migrate:
                    continue
                handler = node.attrib.get('handler')
                assert handler.startswith('.')
                package = path.parent.relpath(self.buildout_dir).replace('/', '.')
                handler = package + handler
                handler_by_profile[profile] = handler
                node.getparent().remove(node)
                changes = True

            if changes:
                prettywrite(path, doc)

        handlers = map(
            itemgetter(1),
            sorted(handler_by_profile.items(),
                   key=lambda item: self.profiles_to_migrate.index(item[0])))

        target_hooks = self.opengever_dir.joinpath('core', 'hooks.py')
        hooks_lines = map(
            lambda handler: 'import {}'.format(handler.rsplit('.', 1)[0]),
            sorted(handlers))
        hooks_lines.extend([target_hooks.bytes().strip()])
        hooks_lines.extend(map('    {}(site)'.format, handlers))

        code = '\n'.join(hooks_lines) + '\n'
        code = code.replace(
            'FORBIDDEN_PROFILES = ()',
            "FORBIDDEN_PROFILES = (\n    '{}')".format(
                "',\n    '".join(self.profiles_to_migrate)))

        target_hooks.write_bytes(code)

    @step('Install the new profile')
    def install_the_new_profile(self):
        path = self.opengever_dir.joinpath('setup/meta.py')
        code = path.bytes()
        code = code.replace("default=u'opengever.policy.base:default'",
                            "default=u'opengever.core:default'")
        path.write_bytes(code)

    @step('Apply patches')
    def apply_patches(self):
        for path in sorted(self.here_dir.joinpath('patches').files()):
            print '-', path.name
            cmd = 'git apply {}'.format(path)
            code = os.system('cd {}; {}'.format(self.buildout_dir, cmd))
            assert code==0, 'patch failed, see above'


    @step('Add upgrade step installing opengever.core:default')
    def add_upgrade_step(self):
        upgrades_dir = self.opengever_dir.joinpath('policy/base/upgrades')
        message = 'Install opengever.core:default after profile merge.'
        step_dir = UpgradeStepCreator(upgrades_dir).create(message)
        upgrade_path = step_dir.joinpath('upgrade.py')
        code = upgrade_path.bytes()
        code += '\n'.join((
            '',
            '        profileid = \'opengever.core:default\'',
            '        if not self.is_profile_installed(profileid):',
            '            self.portal_setup.setLastVersionForProfile(profileid, \'1\')',
            '',
            '        product = \'opengever.core\'',
            '        if not self.is_profile_installed(\'opengever.core\'):',
            '            quickinstaller = self.getToolByName(\'portal_quickinstaller\')',
            '            quickinstaller.notifyInstalled(',
            '                product,',
            '                installedversion=quickinstaller.getProductVersion(product),',
            '                status=\'installed\')',
        ))
        upgrade_path.write_bytes(code)

    @step('Add .gitkeep to old profiles.')
    def keep_old_profiles(self):
        for directory in map(self.profile_path, self.profiles_to_migrate):
            directory.joinpath('.gitkeep').touch()

    def standard_migrate_xml(self, filename):
        with self.og_core_profile_dir.joinpath(filename).open() as fio:
            target = etree.parse(fio)

        for path in self.find_file_in_profiles_to_migrate(filename):
            with path.open() as fio:
                doc = etree.parse(fio)

            self.add_source_comment(target.getroot(), path)
            map(target.getroot().append, doc.getroot().getchildren())
            path.unlink()

        prettywrite(self.og_core_profile_dir.joinpath(filename), target)

    def first_level_tag_xml_migration(self, filename, expressions):
        target_path = self.og_core_profile_dir.joinpath(filename)
        target = parsexml(target_path)
        source_paths = self.find_file_in_profiles_to_migrate(filename)
        sources = map(parsexml, source_paths)
        for expression in expressions:
            self.migrate_first_level_children_node(
                expression, target, zip(source_paths, sources))

        prettywrite(target_path, target)
        did_not_migrate_tags = set()

        for doc in sources:
            map(did_not_migrate_tags.add,
                map(attrgetter('tag'),
                    filter(lambda node: not isinstance(node, etree._Comment),
                           doc.getroot().getchildren())))

        assert not did_not_migrate_tags, \
            '{} didnt migrate tags {!r}'.format(
                filename,
                tuple(did_not_migrate_tags))

        map(methodcaller('unlink'), source_paths)

    def migrate_first_level_children_node(self, expression, target, sources):
        target_node = xpath_one(target, expression)

        for path, source in sources:
            source_node = xpath_one(source, expression, None)
            if source_node is None or len(source_node.getchildren()) == 0:
                continue

            self.add_source_comment(target_node, path)
            map(target_node.append, source_node.getchildren())
            source_node.getparent().remove(source_node)

    def find_file_in_profiles_to_migrate(self, filename):
        return filter(methodcaller('isfile'),
                      map(methodcaller('joinpath', filename),
                          map(self.profile_path, self.profiles_to_migrate)))

    def find_dir_in_profiles_to_migrate(self, filename):
        return filter(methodcaller('isdir'),
                      map(methodcaller('joinpath', filename),
                          map(self.profile_path, self.profiles_to_migrate)))

    @property
    @instance.memoize
    def profiles_to_migrate(self):
        result = []
        for profile in self.recursive_dependencies('opengever.policy.base:default'):
            if not profile.startswith('opengever.'):
                continue
            elif profile in result:
                print '   WARNING: skipping duplicate profile', profile
            else:
                result.append(profile)

        result.append('opengever.policy.base:default')
        return result

    def profile_path(self, profile):
        profile = re.sub('^profile-', '', profile)
        return (self.buildout_dir
                .joinpath(*profile.split(':')[0].split('.'))
                .joinpath('profiles', profile.split(':')[1])).abspath()

    @instance.memoize
    def recursive_dependencies(self, profile):
        result = []

        def recurse(profile):
            result.append(profile)
            if profile.startswith('opengever.'):
                map(recurse, self.read_dependencies(profile))

        recurse(profile)
        result.remove(profile)

        deduplicated = []
        for profile in result:
            if profile in deduplicated:
                deduplicated.remove(profile)

            deduplicated.append(profile)

        return deduplicated


    @instance.memoize
    def read_dependencies(self, profile):
        metadata_xml_path = (self.profile_path(profile)
                             .joinpath('metadata.xml'))
        return self.dependencies_in(metadata_xml_path)

    def dependencies_in(self, metadata_file):
        if not metadata_file.isfile() and metadata_file.parent.isdir():
            return []

        doc = parsexml(metadata_file)
        result = []
        for node in doc.xpath('//dependency'):
            result.append(re.sub('^profile-', '', node.text.strip()))

        return result

    def add_source_comment(self, node, path):
        if node.getchildren():
            node.getchildren()[-1].tail = '\n\n\n'
        else:
            node.text = '\n\n'

        node.append(etree.Comment('migrated from {}'.format(
            path.relpath(self.buildout_dir))))


def prettyformat(xmldoc):
    original = etree.tostring(xmldoc)

    def set_indentation(elem, level=0):
        def indent(text, level):
            text = (text or '').replace('\t', '    ').rstrip(' ')
            if '\n' not in text:
                text += '\n'
            return text + (level * XML_CHILD_INDENT * ' ')

        if len(elem):
            elem.text = indent(elem.text, level + 1)
            elem.tail = indent(elem.tail, level)

            for child in elem:
                set_indentation(child, level + 1)

            child.tail = indent(child.tail, level)
        elif level:
            elem.tail = indent(elem.tail, level)

    def indent_attributes(match):
        prefix, indent, start, attributes, end = match.groups()
        attr_prefix = '\n' + indent + (' ' * XML_ATTR_INDENT)
        attr_regex = re.compile(r'([^ ]*="[^"]*") ')
        tagname = start.lstrip('<').strip()

        if tagname in XML_FORMAT_ONELINE:
            apply_multiline = False
        elif tagname in XML_FORMAT_MULTILINE:
            apply_multiline = True
        else:
            apply_multiline = len(attr_regex.findall(attributes)) > 0

        if apply_multiline:
            attributes = attr_prefix + attr_regex.sub(
                '\g<1>' + attr_prefix, attributes)
        return ''.join((prefix, indent, start, attributes, end))

    set_indentation(xmldoc.getroot())
    xml = etree.tostring(xmldoc, pretty_print=True)
    xml = re.sub('(\n?)( *)(\<[^ /!>]+ )([^>]*)(\/?>)',
                 indent_attributes, xml)

    assert_unchanged(original, xml,
                     'Unexpected difference detected when prettyfing XML')
    return xml


def parsexml(path):
    with path.open() as fio:
        return etree.parse(fio)


def assert_unchanged(expected, got, message):
    expected = c14n(expected)
    got = c14n(got)
    assert got == expected, \
        message + '\n\n' + ''.join((difflib.ndiff(expected.splitlines(1),
                                                  got.splitlines(1))))


def c14n(xmlstring):
    output = StringIO()
    parser = etree.XMLParser(remove_blank_text=True)
    etree.parse(StringIO(xmlstring), parser).write_c14n(output)
    return output.getvalue().strip()



def prettywrite(target, doc):
    target.write_bytes(prettyformat(doc))


if __name__ == '__main__':
    MergeTool()()