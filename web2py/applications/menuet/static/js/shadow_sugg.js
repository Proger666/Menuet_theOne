!function (e, t) {
    "object" == typeof exports && "undefined" != typeof module ? t(require("jquery")) : "function" == typeof define && define.amd ? define(["jquery"], t) : t(e.jQuery)
}(this, function (e) {
    "use strict";

    function t(e, t) {
        var n = e.data && e.data[t];
        return n && new RegExp("^" + m.escapeRegExChars(n) + "([" + p + "]|$)", "i").test(e.value)
    }

    function n(e, t) {
        return x.test(t) && !x.test(e) ? t : e
    }

    function i(e, t, i, s, o) {
        var a = this;
        return n(a.highlightMatches(e, i, s, o), a.highlightMatches(t, i, s, o))
    }

    function s(t, n) {
        var i = this;
        i.element = t, i.el = e(t), i.suggestions = [], i.badQueries = [], i.selectedIndex = -1, i.currentValue = i.element.value, i.intervalId = 0, i.cachedResponse = {}, i.enrichmentCache = {}, i.currentRequest = null, i.inputPhase = e.Deferred(), i.fetchPhase = e.Deferred(), i.enrichPhase = e.Deferred(), i.onChangeTimeout = null, i.triggering = {}, i.$wrapper = null, i.options = e.extend({}, v, n), i.classes = {
            hint: "suggestions-hint",
            mobile: "suggestions-mobile",
            nowrap: "suggestions-nowrap",
            selected: "suggestions-selected",
            suggestion: "suggestions-suggestion",
            subtext: "suggestions-subtext",
            subtext_inline: "suggestions-subtext suggestions-subtext_inline",
            subtext_delimiter: "suggestions-subtext-delimiter",
            subtext_label: "suggestions-subtext suggestions-subtext_label",
            removeConstraint: "suggestions-remove",
            value: "suggestions-value"
        }, i.disabled = !1, i.selection = null, i.$viewport = e(window), i.$body = e(document.body), i.type = null, i.status = {}, i.setupElement(), i.initializer = e.Deferred(), i.el.is(":visible") ? i.initializer.resolve() : i.deferInitialization(), i.initializer.done(e.proxy(i.initialize, i))
    }

    function o() {
        e.each(T, function () {
            this.abort()
        }), T = {}
    }

    function a() {
        L = null, v.geoLocation = B
    }

    function r(t) {
        return e.map(t, function (e) {
            var t = m.escapeHtml(e.text);
            return t && e.matched && (t = "<strong>" + t + "</strong>"), t
        }).join("")
    }

    function u(t, n) {
        var i = t.split(", ");
        return 1 === i.length ? t : e.map(i, function (e) {
            return '<span class="' + n + '">' + e + "</span>"
        }).join(", ")
    }

    function l(t, n) {
        var i = !1;
        return e.each(t, function (e, t) {
            if (i = t.value == n.value && t != n) return !1
        }), i
    }

    function c(t, n) {
        var i = n.selection,
            s = i && i.data && n.bounds;
        return s && e.each(n.bounds.all, function (e, n) {
            return s = i.data[n] === t.data[n]
        }), s
    }

    e = e && e.hasOwnProperty("default") ? e.default : e;
    var d = {
            ENTER: 13,
            ESC: 27,
            TAB: 9,
            SPACE: 32,
            UP: 38,
            DOWN: 40
        },
        f = ".suggestions",
        p = "\\s\"'~\\*\\.,:\\|\\[\\]\\(\\)\\{\\}<>№",
        g = new RegExp("[" + p + "]+", "g"),
        h = new RegExp("[\\-\\+\\/\\\\\\?!@#$%^&]+", "g"),
        m = function () {
            var t = 0;
            return {
                escapeRegExChars: function (e) {
                    return e.replace(/[\-\[\]\/\{\}\(\)\*\+\?\.\\\^\$\|]/g, "\\$&")
                },
                escapeHtml: function (t) {
                    var n = {
                        "&": "&amp;",
                        "<": "&lt;",
                        ">": "&gt;",
                        '"': "&quot;",
                        "'": "&#x27;",
                        "/": "&#x2F;"
                    };
                    return t && e.each(n, function (e, n) {
                        t = t.replace(new RegExp(e, "g"), n)
                    }), t
                },
                getDefaultType: function () {
                    return e.support.cors ? "POST" : "GET"
                },
                getDefaultContentType: function () {
                    return e.support.cors ? "application/json" : "application/x-www-form-urlencoded"
                },
                fixURLProtocol: function (t) {
                    return e.support.cors ? t : t.replace(/^https?:/, location.protocol)
                },
                addUrlParams: function (t, n) {
                    return t + (/\?/.test(t) ? "&" : "?") + e.param(n)
                },
                serialize: function (t) {
                    return e.support.cors ? JSON.stringify(t, function (e, t) {
                        return null === t ? void 0 : t
                    }) : (t = this.compactObject(t), e.param(t, !0))
                },
                compact: function (t) {
                    return e.grep(t, function (e) {
                        return !!e
                    })
                },
                delay: function (e, t) {
                    return setTimeout(e, t || 0)
                },
                uniqueId: function (e) {
                    return (e || "") + ++t
                },
                slice: function (e, t) {
                    return Array.prototype.slice.call(e, t)
                },
                indexBy: function (t, n, i) {
                    var s = {};
                    return e.each(t, function (t, o) {
                        var a = o[n],
                            r = {};
                        i && (r[i] = t), s[a] = e.extend(!0, r, o)
                    }), s
                },
                areSame: function t(n, i) {
                    var s = !0;
                    return typeof n == typeof i && ("object" == typeof n && null != n && null != i ? (e.each(n, function (e, n) {
                        return s = t(n, i[e])
                    }), s) : n === i)
                },
                arrayMinus: function (t, n) {
                    return n ? e.grep(t, function (t, i) {
                        return -1 === e.inArray(t, n)
                    }) : t
                },
                arrayMinusWithPartialMatching: function (t, n) {
                    return n ? e.grep(t, function (e, t) {
                        return !n.some(function (t) {
                            return 0 === t.indexOf(e)
                        })
                    }) : t
                },
                arraysIntersection: function (t, n) {
                    var i = [];
                    return e.isArray(t) && e.isArray(n) ? (e.each(t, function (t, s) {
                        e.inArray(s, n) >= 0 && i.push(s)
                    }), i) : i
                },
                getWords: function (e, t) {
                    e = e.replace(/(\d+)([а-яА-ЯёЁ]{2,})/g, "$1 $2").replace(/([а-яА-ЯёЁ]+)(\d+)/g, "$1 $2");
                    var n = this.compact(e.split(g)),
                        i = n.pop(),
                        s = this.arrayMinus(n, t);
                    return s.push(i), s
                },
                normalize: function (e, t) {
                    return this.getWords(e, t).join(" ")
                },
                stringEncloses: function (e, t) {
                    return e.length > t.length && -1 !== e.indexOf(t)
                },
                fieldsNotEmpty: function (t, n) {
                    if (!e.isPlainObject(t)) return !1;
                    var i = !0;
                    return e.each(n, function (e, n) {
                        return i = !!t[n]
                    }), i
                },
                getDeepValue: function e(t, n) {
                    var i = n.split("."),
                        s = i.shift();
                    return t && (i.length ? e(t[s], i.join(".")) : t[s])
                },
                reWordExtractor: function () {
                    return new RegExp("([^" + p + "]*)([" + p + "]*)", "g")
                },
                getTokens: function (e, t) {
                    var n, i;
                    return n = this.compact(this.formatToken(e).split(g)), i = this.arrayMinus(n, t), n = this.withSubTokens(i.concat(this.arrayMinus(n, i)))
                },
                formatToken: function (e) {
                    return e && e.toLowerCase().replace(/[ёЁ]/g, "е")
                },
                withSubTokens: function (t) {
                    var n = [];
                    return e.each(t, function (e, t) {
                        var i = t.split(h);
                        n.push(t), i.length > 1 && (n = n.concat(m.compact(i)))
                    }), n
                },
                objectKeys: function (t) {
                    if (Object.keys) return Object.keys(t);
                    var n = [];
                    return e.each(t, function (e) {
                        n.push(e)
                    }), n
                },
                compactObject: function (t) {
                    var n = e.extend(!0, {}, t);
                    return e.each(n, function (e, t) {
                        null !== t && void 0 !== t && "" !== t || delete n[e]
                    }), n
                }
            }
        }(),
        y = function () {
            function t(t) {
                return function (n) {
                    if (0 === n.length) return !1;
                    if (1 === n.length) return !0;
                    var i = t(n[0].value);
                    return 0 === e.grep(n, function (e) {
                        return 0 === t(e.value).indexOf(i)
                    }, !0).length
                }
            }

            var n = t(function (e) {
                    return e
                }),
                i = t(function (e) {
                    return e.replace(/, (?:д|вл|двлд|к) .+$/, "")
                });
            return {
                matchByNormalizedQuery: function (t, n) {
                    var i = t.toLowerCase(),
                        s = this && this.stopwords,
                        o = m.normalize(i, s),
                        a = [];
                    return e.each(n, function (e, t) {
                        var n = t.value.toLowerCase();
                        return !m.stringEncloses(i, n) && (!(n.indexOf(o) > 0) && void(o === m.normalize(n, s) && a.push(e)))
                    }), 1 === a.length ? a[0] : -1
                },
                matchByWords: function (t, i) {
                    var s, o = this && this.stopwords,
                        a = t.toLowerCase(),
                        r = [];
                    return n(i) && (s = m.withSubTokens(m.getWords(a, o)), e.each(i, function (e, t) {
                        var n = t.value.toLowerCase();
                        if (m.stringEncloses(a, n)) return !1;
                        var i = m.withSubTokens(m.getWords(n, o));
                        0 === m.arrayMinus(s, i).length && r.push(e)
                    })), 1 === r.length ? r[0] : -1
                },
                matchByWordsAddress: function (t, n) {
                    var s, o = this && this.stopwords,
                        a = t.toLowerCase(),
                        r = -1;
                    return i(n) && (s = m.withSubTokens(m.getWords(a, o)), e.each(n, function (e, t) {
                        var n = t.value.toLowerCase();
                        if (m.stringEncloses(a, n)) return !1;
                        var i = m.withSubTokens(m.getWords(n, o));
                        return 0 === m.arrayMinus(s, i).length ? (r = e, !1) : void 0
                    })), r
                },
                matchByFields: function (t, n) {
                    var i = this && this.stopwords,
                        s = this && this.fieldsStopwords,
                        o = m.withSubTokens(m.getWords(t.toLowerCase(), i)),
                        a = [];
                    return 1 === n.length && (s && e.each(s, function (e, t) {
                        var i = m.getDeepValue(n[0], e),
                            s = i && m.withSubTokens(m.getWords(i.toLowerCase(), t));
                        s && s.length && (a = a.concat(s))
                    }), 0 === m.arrayMinusWithPartialMatching(o, a).length) ? 0 : -1
                }
            }
        }(),
        v = {
            autoSelectFirst: !1,
            serviceUrl: "https://127.0.0.1:8000/menuet/menu_works/api",
            url: null,
            onSearchStart: e.noop,
            onSearchComplete: e.noop,
            onSearchError: e.noop,
            onSuggestionsFetch: null,
            onSelect: null,
            onSelectNothing: null,
            onInvalidateSelection: null,
            minChars: 1,
            deferRequestBy: 100,
            params: {},
            paramName: "query",
            timeout: 3e3,
            formatResult: null,
            formatSelected: null,
            noCache: !1,
            containerClass: "suggestions-suggestions",
            tabDisabled: !1,
            triggerSelectOnSpace: !1,
            triggerSelectOnEnter: !0,
            triggerSelectOnBlur: !0,
            preventBadQueries: !1,
            hint: "Выберите вариант или продолжите ввод",
            noSuggestionsHint: null,
            type: null,
            requestMode: "suggest",
            count: 5,
            $helpers: null,
            headers: null,
            scrollOnFocus: !0,
            mobileWidth: 980,
            initializeInterval: 100
        },
        b = ["ао", "аобл", "дом", "респ", "а/я", "аал", "автодорога", "аллея", "арбан", "аул", "б-р", "берег", "бугор", "вал", "вл", "волость", "въезд", "высел", "г", "городок", "гск", "д", "двлд", "днп", "дор", "дп", "ж/д_будка", "ж/д_казарм", "ж/д_оп", "ж/д_платф", "ж/д_пост", "ж/д_рзд", "ж/д_ст", "жилзона", "жилрайон", "жт", "заезд", "заимка", "зона", "к", "казарма", "канал", "кв", "кв-л", "км", "кольцо", "комн", "кордон", "коса", "кп", "край", "линия", "лпх", "м", "массив", "местность", "мкр", "мост", "н/п", "наб", "нп", "обл", "округ", "остров", "оф", "п", "п/о", "п/р", "п/ст", "парк", "пгт", "пер", "переезд", "пл", "пл-ка", "платф", "погост", "полустанок", "починок", "пр-кт", "проезд", "промзона", "просек", "просека", "проселок", "проток", "протока", "проулок", "р-н", "рзд", "россия", "рп", "ряды", "с", "с/а", "с/мо", "с/о", "с/п", "с/с", "сад", "сквер", "сл", "снт", "спуск", "ст", "ст-ца", "стр", "тер", "тракт", "туп", "у", "ул", "уч-к", "ф/х", "ферма", "х", "ш", "бульвар", "владение", "выселки", "гаражно-строительный", "город", "деревня", "домовладение", "дорога", "квартал", "километр", "комната", "корпус", "литер", "леспромхоз", "местечко", "микрорайон", "набережная", "область", "переулок", "платформа", "площадка", "площадь", "поселение", "поселок", "проспект", "разъезд", "район", "республика", "село", "сельсовет", "слобода", "сооружение", "станица", "станция", "строение", "территория", "тупик", "улица", "улус", "участок", "хутор", "шоссе"],
        _ = [{
            id: "kladr_id",
            fields: ["kladr_id"],
            forBounds: !1,
            forLocations: !0
        }, {
            id: "postal_code",
            fields: ["postal_code"],
            forBounds: !1,
            forLocations: !0
        }, {
            id: "country",
            fields: ["country"],
            forBounds: !1,
            forLocations: !0
        }, {
            id: "region_fias_id",
            fields: ["region_fias_id"],
            forBounds: !1,
            forLocations: !0
        }, {
            id: "region_type_full",
            fields: ["region_type_full"],
            forBounds: !1,
            forLocations: !0,
            kladrFormat: {
                digits: 2,
                zeros: 11
            },
            fiasType: "region_fias_id"
        }, {
            id: "region",
            fields: ["region", "region_type", "region_type_full", "region_with_type"],
            forBounds: !0,
            forLocations: !0,
            kladrFormat: {
                digits: 2,
                zeros: 11
            },
            fiasType: "region_fias_id"
        }, {
            id: "area_fias_id",
            fields: ["area_fias_id"],
            forBounds: !1,
            forLocations: !0
        }, {
            id: "area_type_full",
            fields: ["area_type_full"],
            forBounds: !1,
            forLocations: !0,
            kladrFormat: {
                digits: 5,
                zeros: 8
            },
            fiasType: "area_fias_id"
        }, {
            id: "area",
            fields: ["area", "area_type", "area_type_full", "area_with_type"],
            forBounds: !0,
            forLocations: !0,
            kladrFormat: {
                digits: 5,
                zeros: 8
            },
            fiasType: "area_fias_id"
        }, {
            id: "city_fias_id",
            fields: ["city_fias_id"],
            forBounds: !1,
            forLocations: !0
        }, {
            id: "city_type_full",
            fields: ["city_type_full"],
            forBounds: !1,
            forLocations: !0,
            kladrFormat: {
                digits: 8,
                zeros: 5
            },
            fiasType: "city_fias_id"
        }, {
            id: "city",
            fields: ["city", "city_type", "city_type_full", "city_with_type"],
            forBounds: !0,
            forLocations: !0,
            kladrFormat: {
                digits: 8,
                zeros: 5
            },
            fiasType: "city_fias_id"
        }, {
            id: "city_district_fias_id",
            fields: ["city_district_fias_id"],
            forBounds: !1,
            forLocations: !0
        }, {
            id: "city_district_type_full",
            fields: ["city_district_type_full"],
            forBounds: !1,
            forLocations: !0,
            kladrFormat: {
                digits: 11,
                zeros: 2
            },
            fiasType: "city_district_fias_id"
        }, {
            id: "city_district",
            fields: ["city_district", "city_district_type", "city_district_type_full", "city_district_with_type"],
            forBounds: !0,
            forLocations: !0,
            kladrFormat: {
                digits: 11,
                zeros: 2
            },
            fiasType: "city_district_fias_id"
        }, {
            id: "settlement_fias_id",
            fields: ["settlement_fias_id"],
            forBounds: !1,
            forLocations: !0
        }, {
            id: "settlement_type_full",
            fields: ["settlement_type_full"],
            forBounds: !1,
            forLocations: !0,
            kladrFormat: {
                digits: 11,
                zeros: 2
            },
            fiasType: "settlement_fias_id"
        }, {
            id: "settlement",
            fields: ["settlement", "settlement_type", "settlement_type_full", "settlement_with_type"],
            forBounds: !0,
            forLocations: !0,
            kladrFormat: {
                digits: 11,
                zeros: 2
            },
            fiasType: "settlement_fias_id"
        }, {
            id: "street_fias_id",
            fields: ["street_fias_id"],
            forBounds: !1,
            forLocations: !0
        }, {
            id: "street_type_full",
            fields: ["street_type_full"],
            forBounds: !1,
            forLocations: !0,
            kladrFormat: {
                digits: 15,
                zeros: 2
            },
            fiasType: "street_fias_id"
        }, {
            id: "street",
            fields: ["street", "street_type", "street_type_full", "street_with_type"],
            forBounds: !0,
            forLocations: !0,
            kladrFormat: {
                digits: 15,
                zeros: 2
            },
            fiasType: "street_fias_id"
        }, {
            id: "house",
            fields: ["house", "house_type", "house_type_full", "block", "block_type"],
            forBounds: !0,
            forLocations: !1,
            kladrFormat: {
                digits: 19
            }
        }],
        x = /<strong>/,
        w = {
            LEGAL: [2, 2, 5, 1],
            INDIVIDUAL: [2, 2, 6, 2]
        },
        S = {};
    S.NAME = {
        urlSuffix: "fio",
        noSuggestionsHint: "Неизвестное ФИО",
        matchers: [y.matchByNormalizedQuery, y.matchByWords],
        fieldNames: {
            surname: "фамилия",
            name: "имя",
            patronymic: "отчество"
        },
        isDataComplete: function (n) {
            var i, s = this,
                o = s.options.params,
                a = n.data;
            return e.isFunction(o) && (o = o.call(s.element, n.value)), o && o.parts ? i = e.map(o.parts, function (e) {
                return e.toLowerCase()
            }) : (i = ["surname", "name"], t(n, "surname") && i.push("patronymic")), m.fieldsNotEmpty(a, i)
        },
        composeValue: function (e) {
            return m.compact([e.surname, e.name, e.patronymic]).join(" ")
        }
    }, S.NETWORK = {
        urlSuffix: "network",
        noSuggestionsHint: "Неизвестная сеть",
        matchers: [e.proxy(y.matchByNormalizedQuery, {
            stopwords: b
        }), e.proxy(y.matchByWordsAddress, {
            stopwords: b
        })],
        dataComponents: _,
        dataComponentsById: m.indexBy(_, "id", "index"),
        unformattableTokens: b,
        enrichmentEnabled: !0,
        geoEnabled: !0,
        isDataComplete: function (t) {
            var n = [this.bounds.to || "flat"],
                i = t.data;
            return !e.isPlainObject(i) || m.fieldsNotEmpty(i, n)
        },
        composeValue: function (e, t) {
            var n = e.region_with_type || m.compact([e.region, e.region_type]).join(" ") || e.region_type_full,
                i = e.area_with_type || m.compact([e.area_type, e.area]).join(" ") || e.area_type_full,
                s = e.city_with_type || m.compact([e.city_type, e.city]).join(" ") || e.city_type_full,
                o = e.settlement_with_type || m.compact([e.settlement_type, e.settlement]).join(" ") || e.settlement_type_full,
                a = e.city_district_with_type || m.compact([e.city_district_type, e.city_district]).join(" ") || e.city_district_type_full,
                r = e.street_with_type || m.compact([e.street_type, e.street]).join(" ") || e.street_type_full,
                u = m.compact([e.house_type, e.house, e.block_type, e.block]).join(" "),
                l = m.compact([e.flat_type, e.flat]).join(" "),
                c = e.postal_box && "а/я " + e.postal_box;
            return n === s && (n = ""), t && t.saveCityDistrict || (t && t.excludeCityDistrict ? a = "" : a && !e.city_district_fias_id && (a = "")), m.compact([n, i, s, a, o, r, u, l, c]).join(", ")
        },
        formatResult: function () {
            var t = [],
                n = !1;
            return e.each(_, function () {
                n && t.push(this.id), "city_district" === this.id && (n = !0)
            }),
                function (n, i, s, o) {
                    var a, r, u, l = this,
                        c = s.data && s.data.city_district_with_type,
                        d = o && o.unformattableTokens,
                        f = s.data && s.data.history_values;
                    return f && f.length > 0 && (a = m.getTokens(i, d), r = this.type.findUnusedTokens(a, n), (u = this.type.getFormattedHistoryValues(r, f)) && (n += u)), n = l.highlightMatches(n, i, s, o), n = l.wrapFormattedValue(n, s), c && (!l.bounds.own.length || l.bounds.own.indexOf("street") >= 0) && !e.isEmptyObject(l.copyDataComponents(s.data, t)) && (n += '<div class="' + l.classes.subtext + '">' + l.highlightMatches(c, i, s) + "</div>"), n
                }
        }(),
        findUnusedTokens: function (e, t) {
            var n, i, s = [];
            for (n in e) i = e[n], -1 === t.indexOf(i) && s.push(i);
            return s
        },
        getFormattedHistoryValues: function (e, t) {
            var n, i, s, o, a = [],
                r = "";
            for (s in t) {
                o = t[s];
                for (n in e)
                    if (i = e[n], o.toLowerCase().indexOf(i) >= 0) {
                        a.push(o);
                        break
                    }
            }
            return a.length > 0 && (r = " (бывш. " + a.join(", ") + ")"), r
        },
        getSuggestionValue: function (e, t) {
            var n = null;
            return t.hasSameValues ? n = e.options.restrict_value ? this.getValueWithinConstraints(e, t.suggestion) : e.bounds.own.length ? this.getValueWithinBounds(e, t.suggestion) : t.suggestion.unrestricted_value : t.hasBeenEnriched && e.options.restrict_value && (n = this.getValueWithinConstraints(e, t.suggestion, {
                excludeCityDistrict: !0
            })), n
        },
        getValueWithinConstraints: function (e, t, n) {
            return this.composeValue(e.getUnrestrictedData(t.data), n)
        },
        getValueWithinBounds: function (e, t, n) {
            var i = e.copyDataComponents(t.data, e.bounds.own.concat(["city_district_fias_id"]));
            return this.composeValue(i, n)
        }
    },
        S.M_TAGS = {
            urlSuffix: "m_tags",
            noSuggestionsHint: "Неизвестный тэг",
            matchers: [e.proxy(y.matchByNormalizedQuery, {
                stopwords: b
            }), e.proxy(y.matchByWordsAddress, {
                stopwords: b
            })],
            dataComponents: _,
            dataComponentsById: m.indexBy(_, "id", "index"),
            unformattableTokens: b,
            enrichmentEnabled: !0,
            geoEnabled: !0,
            isDataComplete: function (t) {
                var n = [this.bounds.to || "flat"],
                    i = t.data;
                return !e.isPlainObject(i) || m.fieldsNotEmpty(i, n)
            },
            composeValue: function (e, t) {
                var n = e.region_with_type || m.compact([e.region, e.region_type]).join(" ") || e.region_type_full,
                    i = e.area_with_type || m.compact([e.area_type, e.area]).join(" ") || e.area_type_full,
                    s = e.city_with_type || m.compact([e.city_type, e.city]).join(" ") || e.city_type_full,
                    o = e.settlement_with_type || m.compact([e.settlement_type, e.settlement]).join(" ") || e.settlement_type_full,
                    a = e.city_district_with_type || m.compact([e.city_district_type, e.city_district]).join(" ") || e.city_district_type_full,
                    r = e.street_with_type || m.compact([e.street_type, e.street]).join(" ") || e.street_type_full,
                    u = m.compact([e.house_type, e.house, e.block_type, e.block]).join(" "),
                    l = m.compact([e.flat_type, e.flat]).join(" "),
                    c = e.postal_box && "а/я " + e.postal_box;
                return n === s && (n = ""), t && t.saveCityDistrict || (t && t.excludeCityDistrict ? a = "" : a && !e.city_district_fias_id && (a = "")), m.compact([n, i, s, a, o, r, u, l, c]).join(", ")
            },
            formatResult: function () {
                var t = [],
                    n = !1;
                return e.each(_, function () {
                    n && t.push(this.id), "city_district" === this.id && (n = !0)
                }),
                    function (n, i, s, o) {
                        var a, r, u, l = this,
                            c = s.data && s.data.city_district_with_type,
                            d = o && o.unformattableTokens,
                            f = s.data && s.data.history_values;
                        return f && f.length > 0 && (a = m.getTokens(i, d), r = this.type.findUnusedTokens(a, n), (u = this.type.getFormattedHistoryValues(r, f)) && (n += u)), n = l.highlightMatches(n, i, s, o), n = l.wrapFormattedValue(n, s), c && (!l.bounds.own.length || l.bounds.own.indexOf("street") >= 0) && !e.isEmptyObject(l.copyDataComponents(s.data, t)) && (n += '<div class="' + l.classes.subtext + '">' + l.highlightMatches(c, i, s) + "</div>"), n
                    }
            }(),
            findUnusedTokens: function (e, t) {
                var n, i, s = [];
                for (n in e) i = e[n], -1 === t.indexOf(i) && s.push(i);
                return s
            },
            getFormattedHistoryValues: function (e, t) {
                var n, i, s, o, a = [],
                    r = "";
                for (s in t) {
                    o = t[s];
                    for (n in e)
                        if (i = e[n], o.toLowerCase().indexOf(i) >= 0) {
                            a.push(o);
                            break
                        }
                }
                return a.length > 0 && (r = " (бывш. " + a.join(", ") + ")"), r
            },
            getSuggestionValue: function (e, t) {
                var n = null;
                return t.hasSameValues ? n = e.options.restrict_value ? this.getValueWithinConstraints(e, t.suggestion) : e.bounds.own.length ? this.getValueWithinBounds(e, t.suggestion) : t.suggestion.unrestricted_value : t.hasBeenEnriched && e.options.restrict_value && (n = this.getValueWithinConstraints(e, t.suggestion, {
                    excludeCityDistrict: !0
                })), n
            },
            getValueWithinConstraints: function (e, t, n) {
                return this.composeValue(e.getUnrestrictedData(t.data), n)
            },
            getValueWithinBounds: function (e, t, n) {
                var i = e.copyDataComponents(t.data, e.bounds.own.concat(["city_district_fias_id"]));
                return this.composeValue(i, n)
            }
        },
        S.INGREDIENTS = {
        urlSuffix: "ingredients",
        noSuggestionsHint: "Неизвестный ингредиент",
        matchers: [e.proxy(y.matchByNormalizedQuery, {
            stopwords: b
        }), e.proxy(y.matchByWordsAddress, {
            stopwords: b
        })],
        dataComponents: _,
        dataComponentsById: m.indexBy(_, "id", "index"),
        unformattableTokens: b,
        enrichmentEnabled: !0,
        geoEnabled: !0,
        isDataComplete: function (t) {
            var n = [this.bounds.to || "flat"],
                i = t.data;
            return !e.isPlainObject(i) || m.fieldsNotEmpty(i, n)
        },
        composeValue: function (e, t) {
            var n = e.region_with_type || m.compact([e.region, e.region_type]).join(" ") || e.region_type_full,
                i = e.area_with_type || m.compact([e.area_type, e.area]).join(" ") || e.area_type_full,
                s = e.city_with_type || m.compact([e.city_type, e.city]).join(" ") || e.city_type_full,
                o = e.settlement_with_type || m.compact([e.settlement_type, e.settlement]).join(" ") || e.settlement_type_full,
                a = e.city_district_with_type || m.compact([e.city_district_type, e.city_district]).join(" ") || e.city_district_type_full,
                r = e.street_with_type || m.compact([e.street_type, e.street]).join(" ") || e.street_type_full,
                u = m.compact([e.house_type, e.house, e.block_type, e.block]).join(" "),
                l = m.compact([e.flat_type, e.flat]).join(" "),
                c = e.postal_box && "а/я " + e.postal_box;
            return n === s && (n = ""), t && t.saveCityDistrict || (t && t.excludeCityDistrict ? a = "" : a && !e.city_district_fias_id && (a = "")), m.compact([n, i, s, a, o, r, u, l, c]).join(", ")
        },
        formatResult: function () {
            var t = [],
                n = !1;
            return e.each(_, function () {
                n && t.push(this.id), "city_district" === this.id && (n = !0)
            }),
                function (n, i, s, o) {
                    var a, r, u, l = this,
                        c = s.data && s.data.city_district_with_type,
                        d = o && o.unformattableTokens,
                        f = s.data && s.data.history_values;
                    return f && f.length > 0 && (a = m.getTokens(i, d), r = this.type.findUnusedTokens(a, n), (u = this.type.getFormattedHistoryValues(r, f)) && (n += u)), n = l.highlightMatches(n, i, s, o), n = l.wrapFormattedValue(n, s), c && (!l.bounds.own.length || l.bounds.own.indexOf("street") >= 0) && !e.isEmptyObject(l.copyDataComponents(s.data, t)) && (n += '<div class="' + l.classes.subtext + '">' + l.highlightMatches(c, i, s) + "</div>"), n
                }
        }(),
        findUnusedTokens: function (e, t) {
            var n, i, s = [];
            for (n in e) i = e[n], -1 === t.indexOf(i) && s.push(i);
            return s
        },
        getFormattedHistoryValues: function (e, t) {
            var n, i, s, o, a = [],
                r = "";
            for (s in t) {
                o = t[s];
                for (n in e)
                    if (i = e[n], o.toLowerCase().indexOf(i) >= 0) {
                        a.push(o);
                        break
                    }
            }
            return a.length > 0 && (r = " (бывш. " + a.join(", ") + ")"), r
        },
        getSuggestionValue: function (e, t) {
            var n = null;
            return t.hasSameValues ? n = e.options.restrict_value ? this.getValueWithinConstraints(e, t.suggestion) : e.bounds.own.length ? this.getValueWithinBounds(e, t.suggestion) : t.suggestion.unrestricted_value : t.hasBeenEnriched && e.options.restrict_value && (n = this.getValueWithinConstraints(e, t.suggestion, {
                excludeCityDistrict: !0
            })), n
        },
        getValueWithinConstraints: function (e, t, n) {
            return this.composeValue(e.getUnrestrictedData(t.data), n)
        },
        getValueWithinBounds: function (e, t, n) {
            var i = e.copyDataComponents(t.data, e.bounds.own.concat(["city_district_fias_id"]));
            return this.composeValue(i, n)
        }
    },
        S.I_TAGS = {
            urlSuffix: "i_tags",
            noSuggestionsHint: "Неизвестный тэг",
            matchers: [e.proxy(y.matchByNormalizedQuery, {
                stopwords: b
            }), e.proxy(y.matchByWordsAddress, {
                stopwords: b
            })],
            dataComponents: _,
            dataComponentsById: m.indexBy(_, "id", "index"),
            unformattableTokens: b,
            enrichmentEnabled: !0,
            geoEnabled: !0,
            isDataComplete: function (t) {
                var n = [this.bounds.to || "flat"],
                    i = t.data;
                return !e.isPlainObject(i) || m.fieldsNotEmpty(i, n)
            },
            composeValue: function (e, t) {
                var n = e.region_with_type || m.compact([e.region, e.region_type]).join(" ") || e.region_type_full,
                    i = e.area_with_type || m.compact([e.area_type, e.area]).join(" ") || e.area_type_full,
                    s = e.city_with_type || m.compact([e.city_type, e.city]).join(" ") || e.city_type_full,
                    o = e.settlement_with_type || m.compact([e.settlement_type, e.settlement]).join(" ") || e.settlement_type_full,
                    a = e.city_district_with_type || m.compact([e.city_district_type, e.city_district]).join(" ") || e.city_district_type_full,
                    r = e.street_with_type || m.compact([e.street_type, e.street]).join(" ") || e.street_type_full,
                    u = m.compact([e.house_type, e.house, e.block_type, e.block]).join(" "),
                    l = m.compact([e.flat_type, e.flat]).join(" "),
                    c = e.postal_box && "а/я " + e.postal_box;
                return n === s && (n = ""), t && t.saveCityDistrict || (t && t.excludeCityDistrict ? a = "" : a && !e.city_district_fias_id && (a = "")), m.compact([n, i, s, a, o, r, u, l, c]).join(", ")
            },
            formatResult: function () {
                var t = [],
                    n = !1;
                return e.each(_, function () {
                    n && t.push(this.id), "city_district" === this.id && (n = !0)
                }),
                    function (n, i, s, o) {
                        var a, r, u, l = this,
                            c = s.data && s.data.city_district_with_type,
                            d = o && o.unformattableTokens,
                            f = s.data && s.data.history_values;
                        return f && f.length > 0 && (a = m.getTokens(i, d), r = this.type.findUnusedTokens(a, n), (u = this.type.getFormattedHistoryValues(r, f)) && (n += u)), n = l.highlightMatches(n, i, s, o), n = l.wrapFormattedValue(n, s), c && (!l.bounds.own.length || l.bounds.own.indexOf("street") >= 0) && !e.isEmptyObject(l.copyDataComponents(s.data, t)) && (n += '<div class="' + l.classes.subtext + '">' + l.highlightMatches(c, i, s) + "</div>"), n
                    }
            }(),
            findUnusedTokens: function (e, t) {
                var n, i, s = [];
                for (n in e) i = e[n], -1 === t.indexOf(i) && s.push(i);
                return s
            },
            getFormattedHistoryValues: function (e, t) {
                var n, i, s, o, a = [],
                    r = "";
                for (s in t) {
                    o = t[s];
                    for (n in e)
                        if (i = e[n], o.toLowerCase().indexOf(i) >= 0) {
                            a.push(o);
                            break
                        }
                }
                return a.length > 0 && (r = " (бывш. " + a.join(", ") + ")"), r
            },
            getSuggestionValue: function (e, t) {
                var n = null;
                return t.hasSameValues ? n = e.options.restrict_value ? this.getValueWithinConstraints(e, t.suggestion) : e.bounds.own.length ? this.getValueWithinBounds(e, t.suggestion) : t.suggestion.unrestricted_value : t.hasBeenEnriched && e.options.restrict_value && (n = this.getValueWithinConstraints(e, t.suggestion, {
                    excludeCityDistrict: !0
                })), n
            },
            getValueWithinConstraints: function (e, t, n) {
                return this.composeValue(e.getUnrestrictedData(t.data), n)
            },
            getValueWithinBounds: function (e, t, n) {
                var i = e.copyDataComponents(t.data, e.bounds.own.concat(["city_district_fias_id"]));
                return this.composeValue(i, n)
            }
        }, S.PARTY = {
        urlSuffix: "party",
        noSuggestionsHint: "Неизвестная организация",
        matchers: [e.proxy(y.matchByFields, {
            fieldsStopwords: {
                value: null,
                "data.address.value": b,
                "data.inn": null,
                "data.ogrn": null
            }
        })],
        dataComponents: _,
        geoEnabled: !0,
        formatResult: function (e, t, s, o) {
            var a = this,
                r = a.type.formatResultInn.call(a, s, t),
                u = a.highlightMatches(m.getDeepValue(s.data, "ogrn"), t, s),
                l = n(r, u),
                c = a.highlightMatches(m.getDeepValue(s.data, "management.name"), t, s),
                d = m.getDeepValue(s.data, "address.value") || "";
            return a.isMobile && ((o || (o = {})).maxLength = 50), e = i.call(a, e, m.getDeepValue(s.data, "name.latin"), t, s, o), e = a.wrapFormattedValue(e, s), d && (d = d.replace(/^(\d{6}?\s+|Россия,\s+)/i, ""), d = a.isMobile ? d.replace(new RegExp("^([^" + p + "]+[" + p + "]+[^" + p + "]+).*"), "$1") : a.highlightMatches(d, t, s, {
                unformattableTokens: b
            })), (l || d || c) && (e += '<div class="' + a.classes.subtext + '"><span class="' + a.classes.subtext_inline + '">' + (l || "") + "</span>" + (n(d, c) || "") + "</div>"), e
        },
        formatResultInn: function (t, n) {
            var i, s, o = this,
                a = t.data && t.data.inn,
                r = w[t.data && t.data.type],
                u = /\d/;
            if (a) return s = o.highlightMatches(a, n, t), r && (s = s.split(""), i = e.map(r, function (e) {
                for (var t, n = ""; e && (t = s.shift());) n += t, u.test(t) && e--;
                return n
            }), s = i.join('<span class="' + o.classes.subtext_delimiter + '"></span>') + s.join("")), s
        }
    }, S.EMAIL = {
        urlSuffix: "email",
        noSuggestionsHint: !1,
        matchers: [y.matchByNormalizedQuery],
        isQueryRequestable: function (e) {
            return this.options.suggest_local || e.indexOf("@") >= 0
        }
    }, S.BANK = {
        urlSuffix: "bank",
        noSuggestionsHint: "Неизвестный банк",
        matchers: [e.proxy(y.matchByFields, {
            fieldsStopwords: {
                value: null,
                "data.bic": null,
                "data.swift": null
            }
        })],
        dataComponents: _,
        geoEnabled: !0,
        formatResult: function (e, t, n, i) {
            var s = this,
                o = s.highlightMatches(m.getDeepValue(n.data, "bic"), t, n),
                a = m.getDeepValue(n.data, "address.value") || "";
            return e = s.highlightMatches(e, t, n, i), e = s.wrapFormattedValue(e, n), a && (a = a.replace(/^\d{6}( РОССИЯ)?, /i, ""), a = s.isMobile ? a.replace(new RegExp("^([^" + p + "]+[" + p + "]+[^" + p + "]+).*"), "$1") : s.highlightMatches(a, t, n, {
                unformattableTokens: b
            })), (o || a) && (e += '<div class="' + s.classes.subtext + '"><span class="' + s.classes.subtext_inline + '">' + o + "</span>" + a + "</div>"), e
        },
        formatSelected: function (e) {
            return m.getDeepValue(e, "data.name.payment") || null
        }
    }, e.extend(v, {
        suggest_local: !0
    });
    var C = {
            chains: {},
            on: function (e, t) {
                return this.get(e).push(t), this
            },
            get: function (e) {
                var t = this.chains;
                return t[e] || (t[e] = [])
            }
        },
        k = {
            suggest: {
                defaultParams: {
                    type: m.getDefaultType(),
                    dataType: "json",
                    contentType: m.getDefaultContentType()
                },
                addTypeInUrl: !0
            },
            detectAddressByIp: {
                defaultParams: {
                    type: "GET",
                    dataType: "json"
                },
                addTypeInUrl: !1
            },
            status: {
                defaultParams: {
                    type: "GET",
                    dataType: "json"
                },
                addTypeInUrl: !0
            },
            findById: {
                defaultParams: {
                    type: m.getDefaultType(),
                    dataType: "json",
                    contentType: m.getDefaultContentType()
                },
                addTypeInUrl: !0
            }
        },
        E = {
            suggest: {
                method: "suggest",
                userSelect: !0,
                updateValue: !0,
                enrichmentEnabled: !0
            },
            findById: {
                method: "findById",
                userSelect: !1,
                updateValue: !1,
                enrichmentEnabled: !1
            }
        };
    s.prototype = {
        initialize: function () {
            var e = this;
            e.uniqueId = m.uniqueId("i"), e.createWrapper(), e.notify("initialize"), e.bindWindowEvents(), e.setOptions(), e.fixPosition()
        },
        deferInitialization: function () {
            var e, t = this,
                n = "mouseover focus keydown",
                i = function () {
                    t.initializer.resolve(), t.enable()
                };
            t.initializer.always(function () {
                t.el.off(n, i), clearInterval(e)
            }), t.disabled = !0, t.el.on(n, i), e = setInterval(function () {
                t.el.is(":visible") && i()
            }, t.options.initializeInterval)
        },
        isInitialized: function () {
            return "resolved" === this.initializer.state()
        },
        dispose: function () {
            var e = this;
            e.initializer.reject(), e.notify("dispose"), e.el.removeData("suggestions").removeClass("suggestions-input"), e.unbindWindowEvents(), e.removeWrapper(), e.el.trigger("suggestions-dispose")
        },
        notify: function (t) {
            var n = this,
                i = m.slice(arguments, 1);
            return e.map(C.get(t), function (e) {
                return e.apply(n, i)
            })
        },
        createWrapper: function () {
            var t = this;
            t.$wrapper = e('<div class="suggestions-wrapper"/>'), t.el.after(t.$wrapper), t.$wrapper.on("mousedown" + f, e.proxy(t.onMousedown, t))
        },
        removeWrapper: function () {
            var t = this;
            t.$wrapper && t.$wrapper.remove(), e(t.options.$helpers).off(f)
        },
        onMousedown: function (t) {
            var n = this;
            t.preventDefault(), n.cancelBlur = !0, m.delay(function () {
                delete n.cancelBlur
            }), 0 == e(t.target).closest(".ui-menu-item").length && m.delay(function () {
                e(document).one("mousedown", function (t) {
                    var i = n.el.add(n.$wrapper).add(n.options.$helpers);
                    n.options.floating && (i = i.add(n.$container)), i = i.filter(function () {
                        return this === t.target || e.contains(this, t.target)
                    }), i.length || n.hide()
                })
            })
        },
        bindWindowEvents: function () {
            var t = this,
                n = e.proxy(t.fixPosition, t);
            t.$viewport.on("resize" + f + t.uniqueId, n).on("scroll" + f + t.uniqueId, n)
        },
        unbindWindowEvents: function () {
            this.$viewport.off("resize" + f + this.uniqueId).off("scroll" + f + this.uniqueId)
        },
        scrollToTop: function () {
            var t = this,
                n = t.options.scrollOnFocus;
            !0 === n && (n = t.el), n instanceof e && n.length > 0 && e("body,html").animate({
                scrollTop: n.offset().top
            }, "fast")
        },
        setOptions: function (t) {
            var n = this;
            e.extend(n.options, t), e.each({
                type: S,
                requestMode: E
            }, function (t, i) {
                if (n[t] = i[n.options[t]], !n[t]) throw n.disable(), "`" + t + "` option is incorrect! Must be one of: " + e.map(i, function (e, t) {
                    return '"' + t + '"'
                }).join(", ")
            }), e(n.options.$helpers).off(f).on("mousedown" + f, e.proxy(n.onMousedown, n)), n.isInitialized() && n.notify("setOptions")
        },
        fixPosition: function (t) {
            var n, i, s = this,
                o = {};
            s.isMobile = s.$viewport.width() <= s.options.mobileWidth, s.isInitialized() && (!t || "scroll" != t.type || s.options.floating || s.isMobile) && (s.$container.appendTo(s.options.floating ? s.$body : s.$wrapper), s.notify("resetPosition"), s.el.css("paddingLeft", ""), s.el.css("paddingRight", ""), o.paddingLeft = parseFloat(s.el.css("paddingLeft")), o.paddingRight = parseFloat(s.el.css("paddingRight")), e.extend(o, s.el.offset()), o.borderTop = "none" == s.el.css("border-top-style") ? 0 : parseFloat(s.el.css("border-top-width")), o.borderLeft = "none" == s.el.css("border-left-style") ? 0 : parseFloat(s.el.css("border-left-width")), o.innerHeight = s.el.innerHeight(), o.innerWidth = s.el.innerWidth(), o.outerHeight = s.el.outerHeight(), o.componentsLeft = 0, o.componentsRight = 0, n = s.$wrapper.offset(), i = {
                top: o.top - n.top,
                left: o.left - n.left
            }, s.notify("fixPosition", i, o), o.componentsLeft > o.paddingLeft && s.el.css("paddingLeft", o.componentsLeft + "px"), o.componentsRight > o.paddingRight && s.el.css("paddingRight", o.componentsRight + "px"))
        },
        clearCache: function () {
            this.cachedResponse = {}, this.enrichmentCache = {}, this.badQueries = []
        },
        clear: function () {
            var e = this,
                t = e.selection;
            e.isInitialized() && (e.clearCache(), e.currentValue = "", e.selection = null, e.hide(), e.suggestions = [], e.el.val(""), e.el.trigger("suggestions-clear"), e.notify("clear"), e.trigger("InvalidateSelection", t))
        },
        disable: function () {
            var e = this;
            e.disabled = !0, e.abortRequest(), e.visible && e.hide()
        },
        enable: function () {
            this.disabled = !1
        },
        isUnavailable: function () {
            return this.disabled
        },
        update: function () {
            var e = this,
                t = e.el.val();
            e.isInitialized() && (e.currentValue = t, e.isQueryRequestable(t) ? e.updateSuggestions(t) : e.hide())
        },
        setSuggestion: function (t) {
            var n, i, s = this;
            e.isPlainObject(t) && e.isPlainObject(t.data) && (t = e.extend(!0, {}, t), s.isUnavailable() && s.initializer && "pending" === s.initializer.state() && (s.initializer.resolve(), s.enable()), s.bounds.own.length && (s.checkValueBounds(t), n = s.copyDataComponents(t.data, s.bounds.all), t.data.kladr_id && (n.kladr_id = s.getBoundedKladrId(t.data.kladr_id, s.bounds.all)), t.data = n), s.selection = t, s.suggestions = [t], i = s.getSuggestionValue(t) || "", s.currentValue = i, s.el.val(i), s.abortRequest(), s.el.trigger("suggestions-set"))
        },
        fixData: function () {
            var t = this,
                n = t.extendedCurrentValue(),
                i = t.el.val(),
                s = e.Deferred();
            s.done(function (e) {
                t.selectSuggestion(e, 0, i, {
                    hasBeenEnriched: !0
                }), t.el.trigger("suggestions-fixdata", e)
            }).fail(function () {
                t.selection = null, t.el.trigger("suggestions-fixdata")
            }), t.isQueryRequestable(n) ? (t.currentValue = n, t.getSuggestions(n, {
                count: 1,
                from_bound: null,
                to_bound: null
            }).done(function (e) {
                var t = e[0];
                t ? s.resolve(t) : s.reject()
            }).fail(function () {
                s.reject()
            })) : s.reject()
        },
        extendedCurrentValue: function () {
            var t = this,
                n = t.getParentInstance(),
                i = n && n.extendedCurrentValue(),
                s = e.trim(t.el.val());
            return m.compact([i, s]).join(" ")
        },
        getAjaxParams: function (t, n) {
            var i = this,
                o = e.trim(i.options.token),
                a = e.trim(i.options.partner),
                r = i.options.serviceUrl,
                u = i.options.url,
                l = k[t],
                c = e.extend({
                    timeout: i.options.timeout
                }, l.defaultParams),
                d = {};
            return u ? r = u : (/\/$/.test(r) || (r += "/"), r += t, l.addTypeInUrl && (r += "/" + i.type.urlSuffix)), r = m.fixURLProtocol(r), e.support.cors ? (o && (d.Authorization = "Token " + o), a && (d["X-Partner"] = a), d["X-Version"] = s.version, c.headers || (c.headers = {}), c.xhrFields || (c.xhrFields = {}), e.extend(c.headers, i.options.headers, d), c.xhrFields.withCredentials = !1) : (o && (d.token = o), a && (d.partner = a), d.version = s.version, r = m.addUrlParams(r, d)), c.url = r, e.extend(c, n)
        },
        isQueryRequestable: function (e) {
            var t, n = this;
            return t = e.length >= n.options.minChars, t && n.type.isQueryRequestable && (t = n.type.isQueryRequestable.call(n, e)), t
        },
        constructRequestParams: function (t, n) {
            var i = this,
                s = i.options,
                o = e.isFunction(s.params) ? s.params.call(i.element, t) : e.extend({}, s.params);
            return i.type.constructRequestParams && e.extend(o, i.type.constructRequestParams.call(i)), e.each(i.notify("requestParams"), function (t, n) {
                e.extend(o, n)
            }), o[s.paramName] = t, e.isNumeric(s.count) && s.count > 0 && (o.count = s.count), e.extend(o, n)
        },
        updateSuggestions: function (e) {
            var t = this;
            t.fetchPhase = t.getSuggestions(e).done(function (n) {
                t.assignSuggestions(n, e)
            })
        },
        getSuggestions: function (t, n, i) {
            var s, o = this,
                a = o.options,
                r = i && i.noCallbacks,
                u = i && i.useEnrichmentCache,
                l = o.constructRequestParams(t, n),
                c = e.param(l || {}),
                d = e.Deferred();
            return s = o.cachedResponse[c], s && e.isArray(s.suggestions) ? d.resolve(s.suggestions) : o.isBadQuery(t) ? d.reject() : r || !1 !== a.onSearchStart.call(o.element, l) ? o.doGetSuggestions(l).done(function (e) {
                o.processResponse(e) && t == o.currentValue ? (a.noCache || (u ? o.enrichmentCache[t] = e.suggestions[0] : (o.enrichResponse(e, t), o.cachedResponse[c] = e, a.preventBadQueries && 0 === e.suggestions.length && o.badQueries.push(t))), d.resolve(e.suggestions)) : d.reject(), r || a.onSearchComplete.call(o.element, t, e.suggestions)
            }).fail(function (e, n, i) {
                d.reject(), r || "abort" === n || a.onSearchError.call(o.element, t, e, n, i)
            }) : d.reject(), d
        },
        doGetSuggestions: function (t) {
            t.query = t.query.split(",");
            t.query = t.query[t.query.length - 1].trim();
            var n = this,
                i = e.ajax(n.getAjaxParams(n.requestMode.method, {
                    data: m.serialize(t)
                }));
            return n.abortRequest(), n.currentRequest = i, n.notify("request"), i.always(function () {
                n.currentRequest = null, n.notify("request")
            }), i
        },
        isBadQuery: function (t) {
            if (!this.options.preventBadQueries) return !1;
            var n = !1;
            return e.each(this.badQueries, function (e, i) {
                return !(n = 0 === t.indexOf(i))
            }), n
        },
        abortRequest: function () {
            var e = this;
            e.currentRequest && e.currentRequest.abort()
        },
        processResponse: function (t) {
            var n, i = this;
            return !(!t || !e.isArray(t.suggestions)) && (i.verifySuggestionsFormat(t.suggestions), i.setUnrestrictedValues(t.suggestions), e.isFunction(i.options.onSuggestionsFetch) && (n = i.options.onSuggestionsFetch.call(i.element, t.suggestions), e.isArray(n) && (t.suggestions = n)), !0)
        },
        verifySuggestionsFormat: function (t) {
            "string" == typeof t[0] && e.each(t, function (e, n) {
                t[e] = {
                    value: n,
                    data: null
                }
            })
        },
        getSuggestionValue: function (t, n) {
            var i, s = this,
                o = s.options.formatSelected || s.type.formatSelected,
                a = n && n.hasSameValues,
                r = n && n.hasBeenEnriched,
                u = null;
            return e.isFunction(o) && (i = o.call(s, t)), "string" != typeof i && (i = t.value, s.type.getSuggestionValue && null !== (u = s.type.getSuggestionValue(s, {
                suggestion: t,
                hasSameValues: a,
                hasBeenEnriched: r
            })) && (i = u)), i
        },
        hasSameValues: function (t) {
            var n = !1;
            return e.each(this.suggestions, function (e, i) {
                if (i.value === t.value && i !== t) return n = !0, !1
            }), n
        },
        assignSuggestions: function (e, t) {
            var n = this;
            n.suggestions = e, n.notify("assignSuggestions", t)
        },
        shouldRestrictValues: function () {
            var e = this;
            return e.options.restrict_value && e.constraints && 1 == Object.keys(e.constraints).length
        },
        setUnrestrictedValues: function (t) {
            var n = this,
                i = n.shouldRestrictValues(),
                s = n.getFirstConstraintLabel();
            e.each(t, function (e, t) {
                t.unrestricted_value || (t.unrestricted_value = i ? s + ", " + t.value : t.value)
            })
        },
        areSuggestionsSame: function (e, t) {
            return e && t && e.value === t.value && m.areSame(e.data, t.data)
        },
        getNoSuggestionsHint: function () {
            var e = this;
            return !1 !== e.options.noSuggestionsHint && (e.options.noSuggestionsHint || e.type.noSuggestionsHint)
        }
    };
    var P = {
        setupElement: function () {
            this.el.attr("autocomplete", "off").attr("autocorrect", "off").attr("autocapitalize", "off").attr("spellcheck", "false").addClass("suggestions-input").css("box-sizing", "border-box")
        },
        bindElementEvents: function () {
            var t = this;
            t.el.on("keydown" + f, e.proxy(t.onElementKeyDown, t)), t.el.on(["keyup" + f, "cut" + f, "paste" + f, "input" + f].join(" "), e.proxy(t.onElementKeyUp, t)), t.el.on("blur" + f, e.proxy(t.onElementBlur, t)), t.el.on("focus" + f, e.proxy(t.onElementFocus, t))
        },
        unbindElementEvents: function () {
            this.el.off(f)
        },
        onElementBlur: function () {
            var e = this;
            if (e.cancelBlur) return void(e.cancelBlur = !1);
            e.options.triggerSelectOnBlur ? e.isUnavailable() || e.selectCurrentValue({
                noSpace: !0
            }).always(function () {
                e.hide()
            }) : e.hide(), e.fetchPhase.abort && e.fetchPhase.abort()
        },
        onElementFocus: function () {
            var t = this;
            t.cancelFocus || m.delay(e.proxy(t.completeOnFocus, t)), t.cancelFocus = !1
        },
        onElementKeyDown: function (e) {
            var t = this;
            if (!t.isUnavailable())
                if (t.visible) {
                    switch (e.which) {
                        case d.ESC:
                            t.el.val(t.currentValue), t.hide(), t.abortRequest();
                            break;
                        case d.TAB:
                            if (!1 === t.options.tabDisabled) return;
                            break;
                        case d.ENTER:
                            t.options.triggerSelectOnEnter && t.selectCurrentValue();
                            break;
                        case d.SPACE:
                            return void(t.options.triggerSelectOnSpace && t.isCursorAtEnd() && (e.preventDefault(), t.selectCurrentValue({
                                continueSelecting: !0,
                                dontEnrich: !0
                            }).fail(function () {
                                t.currentValue += " ", t.el.val(t.currentValue), t.proceedChangedValue()
                            })));
                        case d.UP:
                            t.moveUp();
                            break;
                        case d.DOWN:
                            t.moveDown();
                            break;
                        default:
                            return
                    }
                    e.stopImmediatePropagation(), e.preventDefault()
                } else switch (e.which) {
                    case d.DOWN:
                        t.suggest();
                        break;
                    case d.ENTER:
                        t.options.triggerSelectOnEnter && t.triggerOnSelectNothing()
                }
        },
        onElementKeyUp: function (e) {
            var t = this;
            if (!t.isUnavailable()) {
                switch (e.which) {
                    case d.UP:
                    case d.DOWN:
                    case d.ENTER:
                        return
                }
                clearTimeout(t.onChangeTimeout), t.inputPhase.reject(), t.currentValue !== t.el.val() && t.proceedChangedValue()
            }
        },
        proceedChangedValue: function () {
            var t = this;
            t.abortRequest(), t.inputPhase = e.Deferred().done(e.proxy(t.onValueChange, t)), t.options.deferRequestBy > 0 ? t.onChangeTimeout = m.delay(function () {
                t.inputPhase.resolve()
            }, t.options.deferRequestBy) : t.inputPhase.resolve()
        },
        onValueChange: function () {
            var e, t = this;
            t.selection && (e = t.selection, t.selection = null, t.trigger("InvalidateSelection", e)), t.selectedIndex = -1, t.update(), t.notify("valueChange")
        },
        completeOnFocus: function () {
            var e = this;
            e.isUnavailable() || e.isElementFocused() && (e.fixPosition(), e.update(), e.isMobile && (e.setCursorAtEnd(), e.scrollToTop()))
        },
        isElementFocused: function () {
            return document.activeElement === this.element
        },
        isCursorAtEnd: function () {
            var e, t, n = this,
                i = n.el.val().length;
            try {
                if ("number" == typeof(e = n.element.selectionStart)) return e === i
            } catch (e) {
            }
            return !document.selection || (t = document.selection.createRange(), t.moveStart("character", -i), i === t.text.length)
        },
        setCursorAtEnd: function () {
            var e = this.element;
            try {
                e.selectionEnd = e.selectionStart = e.value.length, e.scrollLeft = e.scrollWidth
            } catch (t) {
                e.value = e.value
            }
        }
    };
    e.extend(s.prototype, P), C.on("initialize", P.bindElementEvents).on("dispose", P.unbindElementEvents);
    var T = {};
    o();
    var V = {
        checkStatus: function () {
            function t(t) {
                e.isFunction(n.options.onSearchError) && n.options.onSearchError.call(n.element, null, o, "error", t)
            }

            var n = this,
                i = e.trim(n.options.token),
                s = n.options.type + i,
                o = T[s];
            o || (o = T[s] = e.ajax(n.getAjaxParams("status"))), o.done(function (i) {
                i.search ? e.extend(n.status, i) : t("Service Unavailable")
            }).fail(function () {
                t(o.statusText)
            })
        }
    };
    s.resetTokens = o, e.extend(s.prototype, V), C.on("setOptions", V.checkStatus);
    var L, B = !0,
        I = {
            checkLocation: function () {
                var t = this,
                    n = t.options.geoLocation;
                t.type.geoEnabled && n && (t.geoLocation = e.Deferred(), e.isPlainObject(n) || e.isArray(n) ? t.geoLocation.resolve(n) : (L || (L = e.ajax(t.getAjaxParams("detectAddressByIp"))), L.done(function (e) {
                    var n = e && e.location && e.location.data;
                    n && n.kladr_id ? t.geoLocation.resolve(n) : t.geoLocation.reject()
                }).fail(function () {
                    t.geoLocation.reject()
                })))
            },
            getGeoLocation: function () {
                return this.geoLocation
            },
            constructParams: function () {
                var t = this,
                    n = {};
                return t.geoLocation && e.isFunction(t.geoLocation.promise) && "resolved" == t.geoLocation.state() && t.geoLocation.done(function (t) {
                    n.locations_boost = e.makeArray(t)
                }), n
            }
        };
    "GET" != m.getDefaultType() && (e.extend(v, {
        geoLocation: B
    }), e.extend(s, {
        resetLocation: a
    }), e.extend(s.prototype, {
        getGeoLocation: I.getGeoLocation
    }), C.on("setOptions", I.checkLocation).on("requestParams", I.constructParams));
    var R = {
        enrichSuggestion: function (t, n) {
            var i = this,
                s = e.Deferred();
            return !i.status.enrich || !i.type.enrichmentEnabled || !i.requestMode.enrichmentEnabled || n && n.dontEnrich ? s.resolve(t) : t.data && null != t.data.qc ? s.resolve(t) : (i.disableDropdown(), i.currentValue = t.unrestricted_value, i.enrichPhase = i.getSuggestions(t.unrestricted_value, {
                count: 1,
                locations: null,
                locations_boost: null,
                from_bound: null,
                to_bound: null
            }, {
                noCallbacks: !0,
                useEnrichmentCache: !0
            }).always(function () {
                i.enableDropdown()
            }).done(function (e) {
                var n = e && e[0];
                s.resolve(n || t, !!n)
            }).fail(function () {
                s.resolve(t)
            }), s)
        },
        enrichResponse: function (t, n) {
            var i = this,
                s = i.enrichmentCache[n];
            s && e.each(t.suggestions, function (e, i) {
                if (i.value === n) return t.suggestions[e] = s, !1
            })
        }
    };
    e.extend(s.prototype, R);
    var D = {
            width: "auto",
            floating: !1
        },
        $ = {
            createContainer: function () {
                var t = this,
                    n = "." + t.classes.suggestion,
                    i = t.options,
                    s = e("<div/>").addClass(i.containerClass).css({
                        position: "absolute",
                        display: "none"
                    });
                t.$container = s, s.on("click" + f, n, e.proxy(t.onSuggestionClick, t))
            },
            removeContainer: function () {
                var e = this;
                e.options.floating && e.$container.remove()
            },
            setContainerOptions: function () {
                var t = this;
                t.$container.off("mousedown.suggestions"), t.options.floating && t.$container.on("mousedown.suggestions", e.proxy(t.onMousedown, t))
            },
            onSuggestionClick: function (t) {
                var n, i = this,
                    s = e(t.target);
                if (!i.dropdownDisabled) {
                    for (i.cancelFocus = !0, i.el.focus(); s.length && !(n = s.attr("data-index"));) s = s.closest("." + i.classes.suggestion);
                    n && !isNaN(n) && i.select(+n)
                }
            },
            setDropdownPosition: function (e, t) {
                var n, i = this,
                    s = i.$viewport.scrollLeft();
                i.isMobile ? (n = i.options.floating ? {
                    left: s + "px",
                    top: t.top + t.outerHeight + "px"
                } : {
                    left: e.left - t.left + s + "px",
                    top: e.top + t.outerHeight + "px"
                }, n.width = i.$viewport.width() + "px") : (n = i.options.floating ? {
                    left: t.left + "px",
                    top: t.top + t.borderTop + t.innerHeight + "px"
                } : {
                    left: e.left + "px",
                    top: e.top + t.borderTop + t.innerHeight + "px"
                }, m.delay(function () {
                    var e = i.options.width;
                    "auto" === e && (e = i.el.outerWidth()), i.$container.outerWidth(e)
                })), i.$container.toggleClass(i.classes.mobile, i.isMobile).css(n), i.containerItemsPadding = t.left + t.borderLeft + t.paddingLeft - s
            },
            setItemsPositions: function () {
                var e = this;
                e.getSuggestionsItems().css("paddingLeft", e.isMobile ? e.containerItemsPadding + "px" : "")
            },
            getSuggestionsItems: function () {
                return this.$container.children("." + this.classes.suggestion)
            },
            toggleDropdownEnabling: function (e) {
                this.dropdownDisabled = !e, this.$container.attr("disabled", !e)
            },
            disableDropdown: function () {
                this.toggleDropdownEnabling(!1)
            },
            enableDropdown: function () {
                this.toggleDropdownEnabling(!0)
            },
            hasSuggestionsToChoose: function () {
                var t = this;
                return t.suggestions.length > 1 || 1 === t.suggestions.length && (!t.selection || e.trim(t.suggestions[0].value) !== e.trim(t.selection.value))
            },
            suggest: function () {
                var t, n = this,
                    i = n.options,
                    s = [];
                if (n.requestMode.userSelect) {
                    if (n.hasSuggestionsToChoose()) t = i.formatResult || n.type.formatResult || n.formatResult, !n.isMobile && i.hint && n.suggestions.length && s.push('<div class="' + n.classes.hint + '">' + i.hint + "</div>"), n.selectedIndex = -1, e.each(n.suggestions, function (e, i) {
                        var o = n.makeSuggestionLabel(n.suggestions, i);
                        i == n.selection && (n.selectedIndex = e), s.push('<div class="' + n.classes.suggestion + '" data-index="' + e + '">'), s.push(t.call(n, i.value, n.currentValue, i, {
                            unformattableTokens: n.type.unformattableTokens
                        })), o && s.push('<span class="' + n.classes.subtext_label + '">' + m.escapeHtml(o) + "</span>"), s.push("</div>")
                    });
                    else {
                        if (n.suggestions.length) return void n.hide();
                        var o = n.getNoSuggestionsHint();
                        if (!o) return void n.hide();
                        s.push('<div class="' + n.classes.hint + '">' + o + "</div>")
                    }
                    n.$container.html(s.join("")), i.autoSelectFirst && -1 === n.selectedIndex && (n.selectedIndex = 0), -1 !== n.selectedIndex && n.getSuggestionsItems().eq(n.selectedIndex).addClass(n.classes.selected), e.isFunction(i.beforeRender) && i.beforeRender.call(n.element, n.$container), n.$container.show(), n.visible = !0, n.fixPosition(), n.setItemsPositions()
                }
            },
            wrapFormattedValue: function (e, t) {
                var n = this,
                    i = m.getDeepValue(t.data, "state.status");
                return '<span class="' + n.classes.value + '"' + (i ? ' data-suggestion-status="' + i + '"' : "") + ">" + e + "</span>"
            },
            formatResult: function (e, t, n, i) {
                var s = this;
                return e = s.highlightMatches(e, t, n, i), s.wrapFormattedValue(e, n)
            },
            highlightMatches: function (t, n, i, s) {
                var o, a, l, c, d, f, p, g = this,
                    h = [],
                    y = s && s.unformattableTokens,
                    v = s && s.maxLength,
                    b = m.reWordExtractor();
                if (!t) return "";
                for (o = m.getTokens(n, y), a = e.map(o, function (e) {
                    return new RegExp("^((.*)([\\-\\+\\/\\\\\\?!@#$%^&]+))?(" + m.escapeRegExChars(e) + ")([^\\-\\+\\/\\\\\\?!@#$%^&]*[\\-\\+\\/\\\\\\?!@#$%^&]*)", "i")
                });
                     (l = b.exec(t)) && l[0];) c = l[1], h.push({
                    text: c,
                    hasUpperCase: c.toLowerCase() !== c,
                    formatted: m.formatToken(c),
                    matchable: !0
                }), l[2] && h.push({
                    text: l[2]
                });
                for (d = 0; d < h.length; d++) f = h[d], !f.matchable || f.matched || -1 !== e.inArray(f.formatted, y) && !f.hasUpperCase || e.each(a, function (e, t) {
                    var n, i = t.exec(f.formatted),
                        s = d + 1;
                    if (i) return i = {
                        before: i[1] || "",
                        beforeText: i[2] || "",
                        beforeDelimiter: i[3] || "",
                        text: i[4] || "",
                        after: i[5] || ""
                    }, i.before && (h.splice(d, 0, {
                        text: f.text.substr(0, i.beforeText.length),
                        formatted: i.beforeText,
                        matchable: !0
                    }, {
                        text: i.beforeDelimiter
                    }), s += 2, n = i.before.length, f.text = f.text.substr(n), f.formatted = f.formatted.substr(n), d--), n = i.text.length + i.after.length, f.formatted.length > n && (h.splice(s, 0, {
                        text: f.text.substr(n),
                        formatted: f.formatted.substr(n),
                        matchable: !0
                    }), f.text = f.text.substr(0, n), f.formatted = f.formatted.substr(0, n)), i.after && (n = i.text.length, h.splice(s, 0, {
                        text: f.text.substr(n),
                        formatted: f.formatted.substr(n)
                    }), f.text = f.text.substr(0, n), f.formatted = f.formatted.substr(0, n)), f.matched = !0, !1
                });
                if (v) {
                    for (d = 0; d < h.length && v >= 0; d++) f = h[d], (v -= f.text.length) < 0 && (f.text = f.text.substr(0, f.text.length + v) + "...");
                    h.length = d
                }
                return p = r(h), u(p, g.classes.nowrap)
            },
            makeSuggestionLabel: function (t, n) {
                var i, s, o = this,
                    a = o.type.fieldNames,
                    r = {},
                    u = m.reWordExtractor(),
                    c = [];
                if (a && l(t, n) && n.data && (e.each(a, function (e) {
                        var t = n.data[e];
                        t && (r[e] = m.formatToken(t))
                    }), !e.isEmptyObject(r))) {
                    for (;
                        (i = u.exec(m.formatToken(n.value))) && (s = i[1]);) e.each(r, function (e, t) {
                        if (t == s) return c.push(a[e]), delete r[e], !1
                    });
                    if (c.length) return c.join(", ")
                }
            },
            hide: function () {
                var e = this;
                e.visible = !1, e.selectedIndex = -1, e.$container.hide().empty()
            },
            activate: function (e) {
                var t, n, i = this,
                    s = i.classes.selected;
                return !i.dropdownDisabled && (n = i.getSuggestionsItems(), n.removeClass(s), i.selectedIndex = e, -1 !== i.selectedIndex && n.length > i.selectedIndex) ? (t = n.eq(i.selectedIndex), t.addClass(s), t) : null
            },
            deactivate: function (e) {
                var t = this;
                t.dropdownDisabled || (t.selectedIndex = -1, t.getSuggestionsItems().removeClass(t.classes.selected), e && t.el.val(t.currentValue))
            },
            moveUp: function () {
                var e = this;
                if (!e.dropdownDisabled) return -1 === e.selectedIndex ? void(e.suggestions.length && e.adjustScroll(e.suggestions.length - 1)) : 0 === e.selectedIndex ? void e.deactivate(!0) : void e.adjustScroll(e.selectedIndex - 1)
            },
            moveDown: function () {
                var e = this;
                if (!e.dropdownDisabled) return e.selectedIndex === e.suggestions.length - 1 ? void e.deactivate(!0) : void e.adjustScroll(e.selectedIndex + 1)
            },
            addPreValue: function (s, o) {
                s.currentValue = s.currentValue.split(",");
                if (s.currentValue.length === 1) {
                    return o.value + ","
                }
                var flag = true;
                s.currentValue = s.currentValue.slice(0, -1);

                s.currentValue.forEach(function (element) {
                    if (element === o.value)
                        flag = false;
                });
                if (flag)
                    return s.currentValue = s.currentValue + "," + o.value + ",";
                else {
                    return s.currentValue.join(",") + ","
                }
            },
            addPrevValue: function (s) {
                s.currentValue = s.currentValue.split(",");
                if (s.currentValue.length === 1)
                    s.currentValue = "";
                else {
                    s.currentValue.pop();
                    s.currentValue = s.currentValue.join(",") + ",";
                }
                return s.currentValue
            },
            adjustScroll: function (e) {
                var t, n, i, s = this,
                    o = s.activate(e),
                    a = s.$container.scrollTop();
                o && o.length && (t = o.position().top, t < 0 ? s.$container.scrollTop(a + t) : (n = t + o.outerHeight(), i = s.$container.innerHeight(), n > i && s.$container.scrollTop(a - i + n)),
                    s.currentValue = s.currentValue)
            }
        };
    e.extend(v, D), e.extend(s.prototype, $), C.on("initialize", $.createContainer).on("dispose", $.removeContainer).on("setOptions", $.setContainerOptions).on("fixPosition", $.setDropdownPosition).on("fixPosition", $.setItemsPositions).on("assignSuggestions", $.suggest);
    var j = {
            addon: null
        },
        F = {
            NONE: "none",
            SPINNER: "spinner",
            CLEAR: "clear"
        },
        O = function (t) {
            var n = this,
                i = e('<span class="suggestions-addon"/>');
            n.owner = t, n.$el = i, n.type = F.NONE, n.visible = !1, n.initialPadding = null, i.on("click", e.proxy(n, "onClick"))
        };
    O.prototype = {
        checkType: function () {
            var t = this,
                n = t.owner.options.addon,
                i = !1;
            e.each(F, function (e, t) {
                if (i = t == n) return !1
            }), i || (n = t.owner.isMobile ? F.CLEAR : F.SPINNER), n != t.type && (t.type = n, t.$el.attr("data-addon-type", n), t.toggle(!0))
        },
        toggle: function (e) {
            var t, n = this;
            switch (n.type) {
                case F.CLEAR:
                    t = !!n.owner.currentValue;
                    break;
                case F.SPINNER:
                    t = !!n.owner.currentRequest;
                    break;
                default:
                    t = !1
            }
            t != n.visible && (n.visible = t, t ? n.show(e) : n.hide(e))
        },
        show: function (e) {
            var t = this,
                n = {
                    opacity: 1
                };
            e ? (t.$el.show().css(n), t.showBackground(!0)) : t.$el.stop(!0, !0).delay(50).queue(function () {
                t.$el.show(), t.showBackground(), t.$el.dequeue()
            }).animate(n, "fast")
        },
        hide: function (e) {
            var t = this,
                n = {
                    opacity: 0
                };
            e && t.$el.hide().css(n), t.$el.stop(!0).animate(n, {
                duration: "fast",
                complete: function () {
                    t.$el.hide(), t.hideBackground()
                }
            })
        },
        fixPosition: function (e, t) {
            var n = this,
                i = t.innerHeight;
            n.checkType(), n.$el.css({
                left: e.left + t.borderLeft + t.innerWidth - i + "px",
                top: e.top + t.borderTop + "px",
                height: i,
                width: i
            }), n.initialPadding = t.paddingRight, n.width = i, n.visible && (t.componentsRight += i)
        },
        showBackground: function (e) {
            var t = this,
                n = t.owner.el,
                i = {
                    paddingRight: t.width
                };
            t.width > t.initialPadding && (t.stopBackground(), e ? n.css(i) : n.animate(i, {
                duration: "fast",
                queue: "addon"
            }).dequeue("addon"))
        },
        hideBackground: function (e) {
            var t = this,
                n = t.owner.el,
                i = {
                    paddingRight: t.initialPadding
                };
            t.width > t.initialPadding && (t.stopBackground(!0), e ? n.css(i) : n.delay(1e3, "addon").animate(i, {
                duration: "fast",
                queue: "addon"
            }).dequeue("addon"))
        },
        stopBackground: function (e) {
            this.owner.el.stop("addon", !0, e)
        },
        onClick: function (e) {
            var t = this;
            t.type == F.CLEAR && t.owner.clear()
        }
    };
    var q = {
        createAddon: function () {
            var e = this,
                t = new O(e);
            e.$wrapper.append(t.$el), e.addon = t
        },
        fixAddonPosition: function (e, t) {
            this.addon.fixPosition(e, t)
        },
        checkAddonType: function () {
            this.addon.checkType()
        },
        checkAddonVisibility: function () {
            this.addon.toggle()
        },
        stopBackground: function () {
            this.addon.stopBackground()
        }
    };
    e.extend(v, j), C.on("initialize", q.createAddon).on("setOptions", q.checkAddonType).on("fixPosition", q.fixAddonPosition).on("clear", q.checkAddonVisibility).on("valueChange", q.checkAddonVisibility).on("request", q.checkAddonVisibility).on("resetPosition", q.stopBackground);
    var A = {
            constraints: null,
            restrict_value: !1
        },
        z = ["region_fias_id", "area_fias_id", "city_fias_id", "city_district_fias_id", "settlement_fias_id", "street_fias_id"],
        M = function (t, n) {
            var i, s, o = this,
                a = {};
            o.instance = n, o.fields = {}, o.specificity = -1, e.isPlainObject(t) && n.type.dataComponents && e.each(n.type.dataComponents, function (e, n) {
                var i = n.id;
                n.forLocations && t[i] && (o.fields[i] = t[i], o.specificity = e)
            }), i = m.objectKeys(o.fields), s = m.arraysIntersection(i, z), s.length ? (e.each(s, function (e, t) {
                a[t] = o.fields[t]
            }), o.fields = a, o.specificity = o.getFiasSpecificity(s)) : o.fields.kladr_id && (o.fields = {
                kladr_id: o.fields.kladr_id
            }, o.specificity = o.getKladrSpecificity(o.fields.kladr_id))
        };
    e.extend(M.prototype, {
        getLabel: function () {
            return this.instance.type.composeValue(this.fields, {
                saveCityDistrict: !0
            })
        },
        getFields: function () {
            return this.fields
        },
        isValid: function () {
            return !e.isEmptyObject(this.fields)
        },
        getKladrSpecificity: function (t) {
            var n, i = -1;
            return this.significantKladr = t.replace(/^(\d{2})(\d*?)(0+)$/g, "$1$2"), n = this.significantKladr.length, e.each(this.instance.type.dataComponents, function (e, t) {
                t.kladrFormat && n === t.kladrFormat.digits && (i = e)
            }), i
        },
        getFiasSpecificity: function (t) {
            var n = -1;
            return e.each(this.instance.type.dataComponents, function (i, s) {
                s.fiasType && e.inArray(s.fiasType, t) > -1 && n < i && (n = i)
            }), n
        },
        containsData: function (t) {
            var n = !0;
            return this.fields.kladr_id ? !!t.kladr_id && 0 === t.kladr_id.indexOf(this.significantKladr) : (e.each(this.fields, function (e, i) {
                return n = !!t[e] && t[e].toLowerCase() === i.toLowerCase()
            }), n)
        }
    }), s.ConstraintLocation = M;
    var W = function (t, n) {
        this.id = m.uniqueId("c"), this.deletable = !!t.deletable, this.instance = n, this.locations = e.map(e.makeArray(t && (t.locations || t.restrictions)), function (e) {
            return new M(e, n)
        }), this.locations = e.grep(this.locations, function (e) {
            return e.isValid()
        }), this.label = t.label, null == this.label && n.type.composeValue && (this.label = e.map(this.locations, function (e) {
            return e.getLabel()
        }).join(", ")), this.label && this.isValid() && (this.$el = e(document.createElement("li")).append(e(document.createElement("span")).text(this.label)).attr("data-constraint-id", this.id), this.deletable && this.$el.append(e(document.createElement("span")).addClass(n.classes.removeConstraint)))
    };
    e.extend(W.prototype, {
        isValid: function () {
            return this.locations.length > 0
        },
        getFields: function () {
            return e.map(this.locations, function (e) {
                return e.getFields()
            })
        }
    });
    var N = {
        createConstraints: function () {
            var t = this;
            t.constraints = {}, t.$constraints = e('<ul class="suggestions-constraints"/>'), t.$wrapper.append(t.$constraints), t.$constraints.on("click", "." + t.classes.removeConstraint, e.proxy(t.onConstraintRemoveClick, t))
        },
        setConstraintsPosition: function (e, t) {
            var n = this;
            n.$constraints.css({
                left: e.left + t.borderLeft + t.paddingLeft + "px",
                top: e.top + t.borderTop + Math.round((t.innerHeight - n.$constraints.height()) / 2) + "px"
            }), t.componentsLeft += n.$constraints.outerWidth(!0) + t.paddingLeft
        },
        onConstraintRemoveClick: function (t) {
            var n = this,
                i = e(t.target).closest("li"),
                s = i.attr("data-constraint-id");
            delete n.constraints[s], n.update(), i.fadeOut("fast", function () {
                n.removeConstraint(s)
            })
        },
        setupConstraints: function () {
            var t, n = this,
                i = n.options.constraints;
            if (!i) return void n.unbindFromParent();
            i instanceof e || "string" == typeof i || "number" == typeof i.nodeType ? (t = e(i), t.is(n.constraints) || (n.unbindFromParent(), t.is(n.el) || (n.constraints = t, n.bindToParent()))) : (n._constraintsUpdating = !0, e.each(n.constraints, e.proxy(n.removeConstraint, n)), e.each(e.makeArray(i), function (e, t) {
                n.addConstraint(t)
            }), n._constraintsUpdating = !1, n.fixPosition())
        },
        filteredLocation: function (t) {
            var n = [],
                i = {};
            if (e.each(this.type.dataComponents, function () {
                    this.forLocations && n.push(this.id)
                }), e.isPlainObject(t) && e.each(t, function (e, t) {
                    t && n.indexOf(e) >= 0 && (i[e] = t)
                }), !e.isEmptyObject(i)) return i.kladr_id ? {
                kladr_id: i.kladr_id
            } : i
        },
        addConstraint: function (e) {
            var t = this;
            e = new W(e, t), e.isValid() && (t.constraints[e.id] = e, e.$el && (t.$constraints.append(e.$el), t._constraintsUpdating || t.fixPosition()))
        },
        removeConstraint: function (e) {
            var t = this;
            delete t.constraints[e], t.$constraints.children('[data-constraint-id="' + e + '"]').remove(), t._constraintsUpdating || t.fixPosition()
        },
        constructConstraintsParams: function () {
            for (var t, n, i = this, s = [], o = i.constraints, a = {}; o instanceof e && (t = o.suggestions()) && !(n = m.getDeepValue(t, "selection.data"));) o = t.constraints;
            return o instanceof e ? (n = new M(n, t).getFields()) && (i.bounds.own.indexOf("city") > -1 && delete n.city_fias_id, a.locations = [n], a.restrict_value = !0) : o && (e.each(o, function (e, t) {
                s = s.concat(t.getFields())
            }), s.length && (a.locations = s, a.restrict_value = i.options.restrict_value)), a
        },
        getFirstConstraintLabel: function () {
            var t = this,
                n = e.isPlainObject(t.constraints) && Object.keys(t.constraints)[0];
            return n ? t.constraints[n].label : ""
        },
        bindToParent: function () {
            var t = this;
            t.constraints.on(["suggestions-select." + t.uniqueId, "suggestions-invalidateselection." + t.uniqueId, "suggestions-clear." + t.uniqueId].join(" "), e.proxy(t.onParentSelectionChanged, t)).on("suggestions-dispose." + t.uniqueId, e.proxy(t.onParentDispose, t))
        },
        unbindFromParent: function () {
            var t = this,
                n = t.constraints;
            n instanceof e && n.off("." + t.uniqueId)
        },
        onParentSelectionChanged: function (e, t, n) {
            ("suggestions-select" !== e.type || n) && this.clear()
        },
        onParentDispose: function (e) {
            this.unbindFromParent()
        },
        getParentInstance: function () {
            return this.constraints instanceof e && this.constraints.suggestions()
        },
        shareWithParent: function (e) {
            var t = this.getParentInstance();
            t && t.type === this.type && !c(e, t) && (t.shareWithParent(e), t.setSuggestion(e))
        },
        getUnrestrictedData: function (t) {
            var n = this,
                i = [],
                s = {},
                o = -1;
            return e.each(n.constraints, function (n, i) {
                e.each(i.locations, function (e, n) {
                    n.containsData(t) && n.specificity > o && (o = n.specificity)
                })
            }), o >= 0 ? (t.region_kladr_id && t.region_kladr_id === t.city_kladr_id && i.push.apply(i, n.type.dataComponentsById.city.fields), e.each(n.type.dataComponents.slice(0, o + 1), function (e, t) {
                i.push.apply(i, t.fields)
            }), e.each(t, function (e, t) {
                -1 === i.indexOf(e) && (s[e] = t)
            })) : s = t, s
        }
    };
    e.extend(v, A), e.extend(s.prototype, N), "GET" != m.getDefaultType() && C.on("initialize", N.createConstraints).on("setOptions", N.setupConstraints).on("fixPosition", N.setConstraintsPosition).on("requestParams", N.constructConstraintsParams).on("dispose", N.unbindFromParent);
    var U = {
        proceedQuery: function (e) {
            var t = this;
            e.length >= t.options.minChars ? t.updateSuggestions(e) : t.hide()
        },
        selectCurrentValue: function (t) {
            var n = this,
                i = e.Deferred();
            return n.inputPhase.resolve(), n.fetchPhase.done(function () {
                var e;
                n.selection && !n.visible ? i.reject() : (e = n.findSuggestionIndex(), n.select(e, t), -1 === e ? i.reject() : i.resolve(e))
            }).fail(function () {
                i.reject()
            }), i
        },
        selectFoundSuggestion: function () {
            var e = this;
            e.requestMode.userSelect || e.select(0)
        },
        findSuggestionIndex: function () {
            var t, n = this,
                i = n.selectedIndex;
            return -1 === i && (t = e.trim(n.el.val())) && e.each(n.type.matchers, function (e, s) {
                return -1 === (i = s(t, n.suggestions))
            }), i
        },

        select: function (t, n) {
            var i, s = this,
                o = s.suggestions[t],
                a = n && n.continueSelecting,
                r = s.currentValue;
            if (!s.triggering.Select) {
                if (!o) return a || s.selection || s.triggerOnSelectNothing(), void s.onSelectComplete(a);
                i,
                    o.value = s.addPreValue(s, o),
                    s.enrichSuggestion(o, n).done(function (o, a) {
                        s.selectSuggestion(o, t, r, e.extend({
                            hasBeenEnriched: a,
                            hasSameValues: i
                        }, n))
                    })
            }
        }, selectSuggestion: function (e, t, n, i) {
            var s = this,
                o = i.continueSelecting,
                a = !s.type.isDataComplete || s.type.isDataComplete.call(s, e),
                r = s.selection;
            s.triggering.Select || (s.type.alwaysContinueSelecting && (o = !0), a && (o = !1), i.hasBeenEnriched && s.suggestions[t] && (s.suggestions[t].data = e.data), s.requestMode.updateValue && (s.checkValueBounds(e), s.currentValue = s.getSuggestionValue(e, i), !s.currentValue || i.noSpace || a || (s.currentValue += " "), s.el.val(s.currentValue)), s.currentValue ? (s.selection = e, s.areSuggestionsSame(e, r) || s.trigger("Select", e, s.currentValue != n), s.requestMode.userSelect && s.onSelectComplete(o)) : (s.selection = null, s.triggerOnSelectNothing()), s.shareWithParent(e))
        }, onSelectComplete: function (e) {
            var t = this;
            e ? (t.selectedIndex = -1, t.updateSuggestions(t.currentValue)) : t.hide()
        }, triggerOnSelectNothing: function () {
            var e = this;
            e.triggering.SelectNothing || e.trigger("SelectNothing", e.currentValue)
        }, trigger: function (t) {
            var n = this,
                i = m.slice(arguments, 1),
                s = n.options["on" + t];
            n.triggering[t] = !0, e.isFunction(s) && s.apply(n.element, i), n.el.trigger.call(n.el, "suggestions-" + t.toLowerCase(), i), n.triggering[t] = !1
        }
    };
    e.extend(s.prototype, U),
        C.on("assignSuggestions", U.selectFoundSuggestion);
    var H = {
            bounds: null
        },
        Q = {
            setupBounds: function () {
                this.bounds = {
                    from: null,
                    to: null
                }
            },
            setBoundsOptions: function () {
                var t, n, i = this,
                    s = [],
                    o = e.trim(i.options.bounds).split("-"),
                    a = o[0],
                    r = o[o.length - 1],
                    u = [],
                    l = [];
                i.type.dataComponents && e.each(i.type.dataComponents, function () {
                    this.forBounds && s.push(this.id)
                }), -1 === e.inArray(a, s) && (a = null), n = e.inArray(r, s), -1 !== n && n !== s.length - 1 || (r = null), (a || r) && (t = !a, e.each(s, function (e, n) {
                    if (n == a && (t = !0), l.push(n), t && u.push(n), n == r) return !1
                })), i.bounds.from = a, i.bounds.to = r, i.bounds.all = l, i.bounds.own = u
            },
            constructBoundsParams: function () {
                var e = this,
                    t = {};
                return e.bounds.from && (t.from_bound = {
                    value: e.bounds.from
                }), e.bounds.to && (t.to_bound = {
                    value: e.bounds.to
                }), t
            },
            checkValueBounds: function (e) {
                var t, n = this;
                if (n.bounds.own.length && n.type.composeValue) {
                    var i = n.bounds.own.slice(0);
                    1 === i.length && "city_district" === i[0] && i.push("city_district_fias_id"), t = n.copyDataComponents(e.data, i), e.value = n.type.composeValue(t)
                }
            },
            copyDataComponents: function (t, n) {
                var i = {},
                    s = this.type.dataComponentsById;
                return s && e.each(n, function (n, o) {
                    e.each(s[o].fields, function (e, n) {
                        null != t[n] && (i[n] = t[n])
                    })
                }), i
            },
            getBoundedKladrId: function (t, n) {
                var i, s = n[n.length - 1];
                return e.each(this.type.dataComponents, function (e, t) {
                    if (t.id === s) return i = t.kladrFormat, !1
                }), t.substr(0, i.digits) + new Array((i.zeros || 0) + 1).join("0")
            }
        };
    e.extend(v, H),
        e.extend(s.prototype, Q),
        C.on("initialize", Q.setupBounds).on("setOptions", Q.setBoundsOptions).on("requestParams", Q.constructBoundsParams),
        s.defaultOptions = v,
        s.version = "17.12.0",
        e.Suggestions = s,
        e.fn.suggestions = function (t, n) {
            return 0 === arguments.length ? this.first().data("suggestions") : this.each(function () {
                var i = e(this),
                    o = i.data("suggestions");
                "string" == typeof t ? o && "function" == typeof o[t] && o[t](n) : (o && o.dispose && o.dispose(), o = new s(this, t), i.data("suggestions", o))
            })
        }
});