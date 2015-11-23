!function(t){"function"==typeof define&&define.amd?define(["jquery"],t):"object"==typeof module&&module.exports?module.exports=function(e,i){return void 0===i&&(i="undefined"!=typeof window?require("jquery"):require("jquery")(e)),t(i),i}:t(jQuery)}(function(t){function e(e,i,n){"string"==typeof n&&(n={className:n}),this.options=v(b,t.isPlainObject(n)?n:{}),this.loadHTML(),this.wrapper=t(u.html),this.options.clickToHide&&this.wrapper.addClass(o+"-hidable"),this.wrapper.data(o,this),this.arrow=this.wrapper.find("."+o+"-arrow"),this.container=this.wrapper.find("."+o+"-container"),this.container.append(this.userContainer),e&&e.length&&(this.elementType=e.attr("type"),this.originalElement=e,this.elem=F(e),this.elem.data(o,this),this.elem.before(this.wrapper)),this.container.hide(),this.run(i)}var i=[].indexOf||function(t){for(var e=0,i=this.length;i>e;e++)if(e in this&&this[e]===t)return e;return-1},n="notify",o=n+"js",r=n+"!blank",s={t:"top",m:"middle",b:"bottom",l:"left",c:"center",r:"right"},a=["l","c","r"],l=["t","m","b"],A=["t","b","l","r"],h={t:"b",m:null,b:"t",l:"r",c:null,r:"l"},c=function(e){var i;return i=[],t.each(e.split(/\W+/),function(t,e){var n;return n=e.toLowerCase().charAt(0),s[n]?i.push(n):void 0}),i},d={},u={name:"core",html:'<div class="'+o+'-wrapper">\n  <div class="'+o+'-arrow"></div>\n <div class="'+o+'-container"></div>\n</div>',css:""},p={"border-radius":["-webkit-","-moz-"]},f=function(t){return d[t]},g=function(e,i){if(!e)throw"Missing Style name";if(!i)throw"Missing Style definition";if(!i.html)throw"Missing Style HTML";var r=d[e];r&&r.cssElem&&(window.console&&console.warn(n+": overwriting style '"+e+"'"),d[e].cssElem.remove()),i.name=e,d[e]=i;var s="";i.classes&&t.each(i.classes,function(e,n){return s+="."+o+"-"+i.name+"-"+e+" {\n",t.each(n,function(e,i){return p[e]&&t.each(p[e],function(t,n){return s+=" "+n+e+": "+i+";\n"}),s+=" "+e+": "+i+";\n"}),s+="}\n"}),i.css&&(s+="/* styles for "+i.name+" */\n"+i.css),s&&(i.cssElem=m(s),i.cssElem.attr("id","notify-"+i.name));var a={},l=t(i.html);w("html",l,a),w("text",l,a),i.fields=a},m=function(e){var i;i=E("style"),i.attr("type","text/css"),t("head").append(i);try{i.html(e)}catch(n){i[0].styleSheet.cssText=e}return i},w=function(e,i,n){var o;return"html"!==e&&(e="text"),o="data-notify-"+e,y(i,"["+o+"]").each(function(){var i;i=t(this).attr(o),i||(i=r),n[i]=e})},y=function(t,e){return t.is(e)?t:t.find(e)},b={clickToHide:!0,autoHide:!0,autoHideDelay:5e3,arrowShow:!0,arrowSize:5,breakNewLines:!0,elementPosition:"bottom",globalPosition:"top right",style:"bootstrap",className:"error",showAnimation:"slideDown",showDuration:400,hideAnimation:"slideUp",hideDuration:200,gap:5},v=function(e,i){var n;return n=function(){},n.prototype=e,t.extend(!0,new n,i)},C=function(e){return t.extend(b,e)},E=function(e){return t("<"+e+"></"+e+">")},x={},F=function(e){var i;return e.is("[type=radio]")&&(i=e.parents("form:first").find("[type=radio]").filter(function(i,n){return t(n).attr("name")===e.attr("name")}),e=i.first()),e},S=function(t,e,i){var n,o;if("string"==typeof i)i=parseInt(i,10);else if("number"!=typeof i)return;if(!isNaN(i))return n=s[h[e.charAt(0)]],o=e,void 0!==t[n]&&(e=s[n.charAt(0)],i=-i),void 0===t[e]?t[e]=i:t[e]+=i,null},D=function(t,e,i){if("l"===t||"t"===t)return 0;if("c"===t||"m"===t)return i/2-e/2;if("r"===t||"b"===t)return i-e;throw"Invalid alignment"},M=function(t){return M.e=M.e||E("div"),M.e.text(t).html()};e.prototype.loadHTML=function(){var e;e=this.getStyle(),this.userContainer=t(e.html),this.userFields=e.fields},e.prototype.show=function(t,e){var i,n,o,r,s;if(n=function(i){return function(){return t||i.elem||i.destroy(),e?e():void 0}}(this),s=this.container.parent().parents(":hidden").length>0,o=this.container.add(this.arrow),i=[],s&&t)r="show";else if(s&&!t)r="hide";else if(!s&&t)r=this.options.showAnimation,i.push(this.options.showDuration);else{if(s||t)return n();r=this.options.hideAnimation,i.push(this.options.hideDuration)}return i.push(n),o[r].apply(o,i)},e.prototype.setGlobalPosition=function(){var e=this.getPosition(),i=e[0],n=e[1],r=s[i],a=s[n],l=i+"|"+n,A=x[l];if(!A){A=x[l]=E("div");var h={};h[r]=0,"middle"===a?h.top="45%":"center"===a?h.left="45%":h[a]=0,A.css(h).addClass(o+"-corner"),t("body").append(A)}return A.append(this.wrapper)},e.prototype.setElementPosition=function(){var e,n,o,r,c,d,u,p,f,g,m,w,y,b,v,C,E,x,F,M,B,H,Q,R,k,U,X,j,T;for(X=this.getPosition(),R=X[0],H=X[1],Q=X[2],m=this.elem.position(),p=this.elem.outerHeight(),w=this.elem.outerWidth(),f=this.elem.innerHeight(),g=this.elem.innerWidth(),T=this.wrapper.position(),c=this.container.height(),d=this.container.width(),x=s[R],M=h[R],B=s[M],u={},u[B]="b"===R?p:"r"===R?w:0,S(u,"top",m.top-T.top),S(u,"left",m.left-T.left),j=["top","left"],b=0,C=j.length;C>b;b++)k=j[b],F=parseInt(this.elem.css("margin-"+k),10),F&&S(u,k,F);if(y=Math.max(0,this.options.gap-(this.options.arrowShow?o:0)),S(u,B,y),this.options.arrowShow){for(o=this.options.arrowSize,n=t.extend({},u),e=this.userContainer.css("border-color")||this.userContainer.css("border-top-color")||this.userContainer.css("background-color")||"white",v=0,E=A.length;E>v;v++)k=A[v],U=s[k],k!==M&&(r=U===x?e:"transparent",n["border-"+U]=o+"px solid "+r);S(u,s[M],o),i.call(A,H)>=0&&S(n,s[H],2*o)}else this.arrow.hide();return i.call(l,R)>=0?(S(u,"left",D(H,d,w)),n&&S(n,"left",D(H,o,g))):i.call(a,R)>=0&&(S(u,"top",D(H,c,p)),n&&S(n,"top",D(H,o,f))),this.container.is(":visible")&&(u.display="block"),this.container.removeAttr("style").css(u),n?this.arrow.removeAttr("style").css(n):void 0},e.prototype.getPosition=function(){var t,e,n,o,r,s,h,d;if(d=this.options.position||(this.elem?this.options.elementPosition:this.options.globalPosition),t=c(d),0===t.length&&(t[0]="b"),e=t[0],i.call(A,e)<0)throw"Must be one of ["+A+"]";return(1===t.length||(n=t[0],i.call(l,n)>=0&&(o=t[1],i.call(a,o)<0))||(r=t[0],i.call(a,r)>=0&&(s=t[1],i.call(l,s)<0)))&&(t[1]=(h=t[0],i.call(a,h)>=0?"m":"l")),2===t.length&&(t[2]=t[1]),t},e.prototype.getStyle=function(t){var e;if(t||(t=this.options.style),t||(t="default"),e=d[t],!e)throw"Missing style: "+t;return e},e.prototype.updateClasses=function(){var e,i;return e=["base"],t.isArray(this.options.className)?e=e.concat(this.options.className):this.options.className&&e.push(this.options.className),i=this.getStyle(),e=t.map(e,function(t){return o+"-"+i.name+"-"+t}).join(" "),this.userContainer.attr("class",e)},e.prototype.run=function(e,i){var n,o,s,a,l;if(t.isPlainObject(i)?t.extend(this.options,i):"string"===t.type(i)&&(this.options.className=i),this.container&&!e)return void this.show(!1);if(this.container||e){o={},t.isPlainObject(e)?o=e:o[r]=e;for(s in o)n=o[s],a=this.userFields[s],a&&("text"===a&&(n=M(n),this.options.breakNewLines&&(n=n.replace(/\n/g,"<br/>"))),l=s===r?"":"="+s,y(this.userContainer,"[data-notify-"+a+l+"]").html(n));this.updateClasses(),this.elem?this.setElementPosition():this.setGlobalPosition(),this.show(!0),this.options.autoHide&&(clearTimeout(this.autohideTimer),this.autohideTimer=setTimeout(this.show.bind(this,!1),this.options.autoHideDelay))}},e.prototype.destroy=function(){return this.wrapper.remove()},t[n]=function(i,o,r){return i&&i.nodeName||i.jquery?t(i)[n](o,r):(r=o,o=i,new e(null,o,r)),i},t.fn[n]=function(i,n){return t(this).each(function(){var r;return r=F(t(this)).data(o),r?r.run(i,n):new e(t(this),i,n)}),this},t.extend(t[n],{defaults:C,addStyle:g,pluginOptions:b,getStyle:f,insertCSS:m}),g("bootstrap",{html:"<div>\n<span data-notify-text></span>\n</div>",classes:{base:{"font-weight":"bold",padding:"8px 15px 8px 14px","text-shadow":"0 1px 0 rgba(255, 255, 255, 0.5)","background-color":"#fcf8e3",border:"1px solid #fbeed5","border-radius":"4px","white-space":"nowrap","padding-left":"25px","background-repeat":"no-repeat","background-position":"3px 7px"},error:{color:"#B94A48","background-color":"#F2DEDE","border-color":"#EED3D7","background-image":"url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAAtRJREFUeNqkVc1u00AQHq+dOD+0poIQfkIjalW0SEGqRMuRnHos3DjwAH0ArlyQeANOOSMeAA5VjyBxKBQhgSpVUKKQNGloFdw4cWw2jtfMOna6JOUArDTazXi/b3dm55socPqQhFka++aHBsI8GsopRJERNFlY88FCEk9Yiwf8RhgRyaHFQpPHCDmZG5oX2ui2yilkcTT1AcDsbYC1NMAyOi7zTX2Agx7A9luAl88BauiiQ/cJaZQfIpAlngDcvZZMrl8vFPK5+XktrWlx3/ehZ5r9+t6e+WVnp1pxnNIjgBe4/6dAysQc8dsmHwPcW9C0h3fW1hans1ltwJhy0GxK7XZbUlMp5Ww2eyan6+ft/f2FAqXGK4CvQk5HueFz7D6GOZtIrK+srupdx1GRBBqNBtzc2AiMr7nPplRdKhb1q6q6zjFhrklEFOUutoQ50xcX86ZlqaZpQrfbBdu2R6/G19zX6XSgh6RX5ubyHCM8nqSID6ICrGiZjGYYxojEsiw4PDwMSL5VKsC8Yf4VRYFzMzMaxwjlJSlCyAQ9l0CW44PBADzXhe7xMdi9HtTrdYjFYkDQL0cn4Xdq2/EAE+InCnvADTf2eah4Sx9vExQjkqXT6aAERICMewd/UAp/IeYANM2joxt+q5VI+ieq2i0Wg3l6DNzHwTERPgo1ko7XBXj3vdlsT2F+UuhIhYkp7u7CarkcrFOCtR3H5JiwbAIeImjT/YQKKBtGjRFCU5IUgFRe7fF4cCNVIPMYo3VKqxwjyNAXNepuopyqnld602qVsfRpEkkz+GFL1wPj6ySXBpJtWVa5xlhpcyhBNwpZHmtX8AGgfIExo0ZpzkWVTBGiXCSEaHh62/PoR0p/vHaczxXGnj4bSo+G78lELU80h1uogBwWLf5YlsPmgDEd4M236xjm+8nm4IuE/9u+/PH2JXZfbwz4zw1WbO+SQPpXfwG/BBgAhCNZiSb/pOQAAAAASUVORK5CYII=)"},success:{color:"#468847","background-color":"#DFF0D8","border-color":"#D6E9C6","background-image":"url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAAutJREFUeNq0lctPE0Ecx38zu/RFS1EryqtgJFA08YCiMZIAQQ4eRG8eDGdPJiYeTIwHTfwPiAcvXIwXLwoXPaDxkWgQ6islKlJLSQWLUraPLTv7Gme32zoF9KSTfLO7v53vZ3d/M7/fIth+IO6INt2jjoA7bjHCJoAlzCRw59YwHYjBnfMPqAKWQYKjGkfCJqAF0xwZjipQtA3MxeSG87VhOOYegVrUCy7UZM9S6TLIdAamySTclZdYhFhRHloGYg7mgZv1Zzztvgud7V1tbQ2twYA34LJmF4p5dXF1KTufnE+SxeJtuCZNsLDCQU0+RyKTF27Unw101l8e6hns3u0PBalORVVVkcaEKBJDgV3+cGM4tKKmI+ohlIGnygKX00rSBfszz/n2uXv81wd6+rt1orsZCHRdr1Imk2F2Kob3hutSxW8thsd8AXNaln9D7CTfA6O+0UgkMuwVvEFFUbbAcrkcTA8+AtOk8E6KiQiDmMFSDqZItAzEVQviRkdDdaFgPp8HSZKAEAL5Qh7Sq2lIJBJwv2scUqkUnKoZgNhcDKhKg5aH+1IkcouCAdFGAQsuWZYhOjwFHQ96oagWgRoUov1T9kRBEODAwxM2QtEUl+Wp+Ln9VRo6BcMw4ErHRYjH4/B26AlQoQQTRdHWwcd9AH57+UAXddvDD37DmrBBV34WfqiXPl61g+vr6xA9zsGeM9gOdsNXkgpEtTwVvwOklXLKm6+/p5ezwk4B+j6droBs2CsGa/gNs6RIxazl4Tc25mpTgw/apPR1LYlNRFAzgsOxkyXYLIM1V8NMwyAkJSctD1eGVKiq5wWjSPdjmeTkiKvVW4f2YPHWl3GAVq6ymcyCTgovM3FzyRiDe2TaKcEKsLpJvNHjZgPNqEtyi6mZIm4SRFyLMUsONSSdkPeFtY1n0mczoY3BHTLhwPRy9/lzcziCw9ACI+yql0VLzcGAZbYSM5CCSZg1/9oc/nn7+i8N9p/8An4JMADxhH+xHfuiKwAAAABJRU5ErkJggg==)"},info:{color:"#3A87AD","background-color":"#D9EDF7","border-color":"#BCE8F1","background-image":"url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAAsTAAALEwEAmpwYAAAAB3RJTUUH3QYFAhkSsdes/QAAA8dJREFUOMvVlGtMW2UYx//POaWHXg6lLaW0ypAtw1UCgbniNOLcVOLmAjHZolOYlxmTGXVZdAnRfXQm+7SoU4mXaOaiZsEpC9FkiQs6Z6bdCnNYruM6KNBw6YWewzl9z+sHImEWv+vz7XmT95f/+3/+7wP814v+efDOV3/SoX3lHAA+6ODeUFfMfjOWMADgdk+eEKz0pF7aQdMAcOKLLjrcVMVX3xdWN29/GhYP7SvnP0cWfS8caSkfHZsPE9Fgnt02JNutQ0QYHB2dDz9/pKX8QjjuO9xUxd/66HdxTeCHZ3rojQObGQBcuNjfplkD3b19Y/6MrimSaKgSMmpGU5WevmE/swa6Oy73tQHA0Rdr2Mmv/6A1n9w9suQ7097Z9lM4FlTgTDrzZTu4StXVfpiI48rVcUDM5cmEksrFnHxfpTtU/3BFQzCQF/2bYVoNbH7zmItbSoMj40JSzmMyX5qDvriA7QdrIIpA+3cdsMpu0nXI8cV0MtKXCPZev+gCEM1S2NHPvWfP/hL+7FSr3+0p5RBEyhEN5JCKYr8XnASMT0xBNyzQGQeI8fjsGD39RMPk7se2bd5ZtTyoFYXftF6y37gx7NeUtJJOTFlAHDZLDuILU3j3+H5oOrD3yWbIztugaAzgnBKJuBLpGfQrS8wO4FZgV+c1IxaLgWVU0tMLEETCos4xMzEIv9cJXQcyagIwigDGwJgOAtHAwAhisQUjy0ORGERiELgG4iakkzo4MYAxcM5hAMi1WWG1yYCJIcMUaBkVRLdGeSU2995TLWzcUAzONJ7J6FBVBYIggMzmFbvdBV44Corg8vjhzC+EJEl8U1kJtgYrhCzgc/vvTwXKSib1paRFVRVORDAJAsw5FuTaJEhWM2SHB3mOAlhkNxwuLzeJsGwqWzf5TFNdKgtY5qHp6ZFf67Y/sAVadCaVY5YACDDb3Oi4NIjLnWMw2QthCBIsVhsUTU9tvXsjeq9+X1d75/KEs4LNOfcdf/+HthMnvwxOD0wmHaXr7ZItn2wuH2SnBzbZAbPJwpPx+VQuzcm7dgRCB57a1uBzUDRL4bfnI0RE0eaXd9W89mpjqHZnUI5Hh2l2dkZZUhOqpi2qSmpOmZ64Tuu9qlz/SEXo6MEHa3wOip46F1n7633eekV8ds8Wxjn37Wl63VVa+ej5oeEZ/82ZBETJjpJ1Rbij2D3Z/1trXUvLsblCK0XfOx0SX2kMsn9dX+d+7Kf6h8o4AIykuffjT8L20LU+w4AZd5VvEPY+XpWqLV327HR7DzXuDnD8r+ovkBehJ8i+y8YAAAAASUVORK5CYII=)"},warn:{color:"#C09853","background-color":"#FCF8E3","border-color":"#FBEED5","background-image":"url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAMAAAC6V+0/AAABJlBMVEXr6eb/2oD/wi7/xjr/0mP/ykf/tQD/vBj/3o7/uQ//vyL/twebhgD/4pzX1K3z8e349vK6tHCilCWbiQymn0jGworr6dXQza3HxcKkn1vWvV/5uRfk4dXZ1bD18+/52YebiAmyr5S9mhCzrWq5t6ufjRH54aLs0oS+qD751XqPhAybhwXsujG3sm+Zk0PTwG6Shg+PhhObhwOPgQL4zV2nlyrf27uLfgCPhRHu7OmLgAafkyiWkD3l49ibiAfTs0C+lgCniwD4sgDJxqOilzDWowWFfAH08uebig6qpFHBvH/aw26FfQTQzsvy8OyEfz20r3jAvaKbhgG9q0nc2LbZxXanoUu/u5WSggCtp1anpJKdmFz/zlX/1nGJiYmuq5Dx7+sAAADoPUZSAAAAAXRSTlMAQObYZgAAAAFiS0dEAIgFHUgAAAAJcEhZcwAACxMAAAsTAQCanBgAAAAHdElNRQfdBgUBGhh4aah5AAAAlklEQVQY02NgoBIIE8EUcwn1FkIXM1Tj5dDUQhPU502Mi7XXQxGz5uVIjGOJUUUW81HnYEyMi2HVcUOICQZzMMYmxrEyMylJwgUt5BljWRLjmJm4pI1hYp5SQLGYxDgmLnZOVxuooClIDKgXKMbN5ggV1ACLJcaBxNgcoiGCBiZwdWxOETBDrTyEFey0jYJ4eHjMGWgEAIpRFRCUt08qAAAAAElFTkSuQmCC)"}}}),t(function(){return m(u.css).attr("id","core-notify"),t(document).on("click","."+o+"-hidable",function(e){return t(this).trigger("notify-hide")}),t(document).on("notify-hide","."+o+"-wrapper",function(e){var i=t(this).data(o);i&&i.show(!1)})})});