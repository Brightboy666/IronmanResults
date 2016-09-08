var CKMLib = (function(){
	var ckmObj = {
		getCookie: function(name, options){
			if (options && options.callback){
				if (!options.attempts)
					options.attempts = 0;
				var cookieValue = ckmObj.getCookieValue(name);
				if ((cookieValue != null || options.attempts++ == (options.max || 50)))
					options.callback(cookieValue);
				else 
					window.setTimeout(function(){
						ckmObj.getCookie(name, options);
					}, (options.ms || 100));
			} else
				return ckmObj.getCookieValue(name);
		},
		getCookieValue: function(name){
			var name_s = name + '=';
			var ca = document.cookie.split(';');
			for (var i = 0; i < ca.length; i++) {
				var c = ca[i];
				while (c.charAt(0) == ' ')
					c = c.substring(1, c.length);
				if (c.indexOf(name_s) == 0)
					return c.substring(name_s.length, c.length);
			}
			return null;
		},
		setCookie: function(name, value, days){
			var expires = '';
			if (days) {
				var d = new Date();
				d.setTime(d.getTime() + (days * 24 * 60 * 60 * 1000));
				expires = '; expires=' + d.toGMTString();
			}
			document.cookie = name + '=' + value + expires + '; path=/';
		},
		removeCookie: function(name){
			ckmObj.setCookie(name, '', -1);
		},
		getQSParams: function(qs){
			if (!qs || typeof qs != "string")
				return {};

			var s = qs.split("&"), params = {};
			for (var i = 0; i < s.length; i++) {
				var nv = s[i].split("=");
				if (nv.length >= 2) {
					var name = decodeURIComponent(nv[0]);
					if (name.length == 0)
						continue;
					var value = decodeURIComponent(nv[1]);
					if (typeof params[name] == "undefined")
						params[name] = value;
					else if (params[name] instanceof Array)
						params[name].push(value);
					else
						params[name] = [params[name], value];
				}
			}
			return params;
		},
		getParam: function (name, referrer_priority) {
			var s_v, keys = (name || '').split(','),
				f_p = referrer_priority && referrer_priority !== -1 ? ckmObj.referrer_qs_params : ckmObj.url_qs_params,
				s_p = referrer_priority && referrer_priority !== -1 ? ckmObj.url_qs_params : (referrer_priority !== -1 ? ckmObj.referrer_qs_params : null);

			for (var i = 0; i < keys.length; i++) {
				if (f_p.hasOwnProperty(keys[i])) return f_p[keys[i]];
				s_v = s_v || ((s_p && s_p.hasOwnProperty(keys[i])) ? s_p[keys[i]] : null);
			}
			return s_v;
		},
		uniqueSession: function(override_keys, referrer_priority){
			var u_p, r_p, keys = override_keys instanceof Array ? override_keys : (override_keys || '').split(',');
			for (var i = 0; i < keys.length; i++) {
				u_p = u_p || ckmObj.url_qs_params[keys[i]];
				r_p = r_p || ckmObj.referrer_qs_params[keys[i]];
			}
			var p = (referrer_priority !== -1 && ((referrer_priority && r_p) || !u_p)) ? r_p : u_p;
			var ex_c = ckmObj.getCookie('CKM_sess');
			if (!ex_c) {
				ckmObj.setCookie('CKM_sess', p || '1');
				return true;
			} else if (p) {
				ckmObj.setCookie('CKM_sess', p);
				return p != ex_c;
			}
			return false;
		},
		clickParamCfg: {},
		clickParams: function(paramCfg){
			this.clickParamCfg = paramCfg;
		},
		eventParamCfg: {},
		eventParams: function(paramCfg){
			this.eventParamCfg = paramCfg;
		},
		getExtraParams: function (params) {
			var extra_params = '';
			if (params) {
				var keys = [];
				var values = [];
				for (var k in params) {
					if (params.hasOwnProperty(k)) {
						keys.push(k);
						values.push(params[k]);
					}
				}

				extra_params = keys.length > 0 ? '&ckmxk=' + encodeURIComponent(keys.join('^')) + '&ckmxv=' + encodeURIComponent(values.join('^')) : '';
			}
			return extra_params;
		},
		insertScript: function(u, async){
			var el = document.createElement('script');
			el.type = 'text/javascript';
			el.src = u;
			el.async = !!async;
			var s = document.getElementsByTagName('script')[0];
			s.parentNode.insertBefore(el, s);
		},
		run: function(c){
			typeof c === 'function' ? c() : ckmObj[c.name](c.args);
		},
		cp: function (a) {
			var ckmreqid = a['ckm_sess_param'] || a[7] || 'ckmreqid';
			var session_override = ckmObj.url_qs_params[ckmreqid];
			var session_override_ref = ckmObj.referrer_qs_params[ckmreqid];
			if (session_override && !ckmObj.getCookie('CKM_sess'))
				ckmObj.setCookie('CKM_sess', session_override);
			if (a instanceof Array && ((session_override && ckmObj.uniqueSession(ckmreqid, -1)) || (!session_override && ckmObj.uniqueSession(a[0], session_override_ref ? -1 : a[1])))) {
				ckmObj.insertScript('//' + a[4] + '/?cp=js&scn=' + encodeURIComponent(ckmObj.getParam(a[2], a[3]) || '') + ckmObj.getExtraParams(ckmObj.clickParamCfg) + (a[6] ? '&c=' + a[6] : '') + '&ckmrt=' + a[5] + '&ckmpg=' + encodeURIComponent(document.URL) + '&ckmref=' + encodeURIComponent(document.referrer));
			} else if (!(a instanceof Array) && ((session_override && ckmObj.uniqueSession(ckmreqid, -1)) || (!session_override && ckmObj.uniqueSession(a['sess_param'], session_override_ref ? -1 : a['sess_chk_ref'])))) {
				ckmObj.insertScript('//' + a['cookie_dom'] + '/?cp=js&scn=' + encodeURIComponent(ckmObj.getParam(a['attr_param'], a['attr_chk_ref']) || '') + ckmObj.getExtraParams(ckmObj.clickParamCfg) + '&c=' + (ckmObj.getParam(a['crtv_param'], a['crtv_chk_ref']) || (a['crtv_id'] ? a['crtv_id'] : '')) + '&ckmrt=' + a['ref_type'] + '&ckmpg=' + encodeURIComponent(document.URL) + '&ckmref=' + encodeURIComponent(document.referrer));
			} else {
				if (session_override) {
					ckmObj.setCookie('ckmsid', session_override);
					var extra_params = ckmObj.getExtraParams(ckmObj.clickParamCfg);
					if (extra_params.length) {
						if (a instanceof Array)
							ckmObj.insertScript('//' + a[4] + '/?cp=jsu&ckmreqid=' + session_override + extra_params + '&ckmrt=' + a[5] + '&ckmpg=' + encodeURIComponent(document.URL) + '&ckmref=' + encodeURIComponent(document.referrer));
						else
							ckmObj.insertScript('//' + a['cookie_dom'] + '/?cp=jsu&ckmreqid=' + session_override + extra_params + '&ckmrt=' + a['ref_type'] + '&ckmpg=' + encodeURIComponent(document.URL) + '&ckmref=' + encodeURIComponent(document.referrer));
					}
				}
				window.ckm_cp = true;
				window.ckm_request_id = ckmObj.getCookie('ckmsid');
			}
		},
		eventCfg: {},
		configureEvents: function(cfg){
			this.eventCfg = cfg;
		},
		fireEvent: function(cfg){
			if (cfg == null || typeof cfg !== 'object') {
				cfg = {
					event_id: cfg,
					transaction_id: arguments.length >= 2 ? arguments[1] : ''
				}
			}
			var u = (cfg.domain || this.eventCfg.domain) + '/p.ashx?f=js';
			
			var ps = [['advertiser_id', 'a'], ['offer_id', 'o'], ['event_id', 'e'], ['request_session_id', 'r'], ['revenue', 'p'], ['transaction_id', 't'], ['sku', 'ecsk'],
				['line_item_quantity', 'ecqu'], ['line_item_price', 'ecpr'], ['line_item_discount', 'ecld'], ['order_sub_total', 'ecst'],
				['order_discount', 'ecd'], ['order_tax', 'ectx'], ['order_shipping', 'ecsh'], ['order_total', 'ect'], ['voucher_code', 'ecv'], ['country', 'ecco'], ['region', 'ecrg']];

			for (var i = 0; i < ps.length; i++) {
				var p = ps[i];
				v = cfg[p[0]] || cfg[p[1]] || this.eventCfg[p[0]] || this.eventCfg[p[1]];
				if (v) u += '&' + p[1] + '=' + encodeURIComponent(v);
			}

			u += this.getExtraParams(cfg.event_params);

			ckmObj.insertScript(u);
		}
	};

	ckmObj.url_qs_params = ckmObj.getQSParams(location.search.substring(1));
	ckmObj.referrer_qs_params = {};
	if (document.referrer && document.referrer.length >= 8) {
		var r = document.referrer.substring(8);
		var idx = r.indexOf('?');
		if (idx == -1) idx = r.lastIndexOf('/');
		if (idx > -1) ckmObj.referrer_qs_params = ckmObj.getQSParams(r.substring(idx + 1));
	}

	return ckmObj;
})();

if (typeof _ckm == 'object' && _ckm instanceof Array) {
	var c;
	while (c = _ckm.shift())
		CKMLib.run(c);
}
else _ckm = [];

_ckm.unshift = _ckm.push = CKMLib.run;
