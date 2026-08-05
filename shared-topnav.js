/* 统一顶部导航：动态注入全站菜单，避免各页面复制出不同版本。 */
(function () {
  "use strict";

  var script = document.currentScript;
  var scriptUrl = new URL(script && script.src ? script.src : "shared-topnav.js", document.baseURI);
  var siteBase = new URL(".", scriptUrl);
  var currentPath = new URL(window.location.href).pathname;
  var siteBasePath = siteBase.pathname;
  var currentKey = currentPath.indexOf(siteBasePath) === 0
    ? currentPath.slice(siteBasePath.length).replace(/^\/+/, "")
    : currentPath.split("/").pop();
  if (!currentKey) currentKey = "index.html";
  if (currentKey === "keyfiles-pages/" || currentKey === "keyfiles-pages/index.html") currentKey = "keyfiles-pages/index.html";

  function page(file) {
    return new URL(file, siteBase).href;
  }

  function link(file, label, icon, group, extraClass) {
    var active = currentKey === file ? " active" : "";
    return '<a class="site-topnav-item' + active + (extraClass ? " " + extraClass : "") + '" data-page="' + file + '" data-group="' + (group || "") + '" href="' + page(file) + '"><span class="site-topnav-icon">' + icon + '</span><span>' + label + '</span></a>';
  }

  function dropdown(label, icon, group, items, right) {
    var active = items.some(function (item) { return currentKey === item[0]; }) ? " active" : "";
    var rightClass = right ? " has-dropdown-right" : "";
    var html = '<div class="site-topnav-item has-dropdown' + rightClass + active + '" data-group="' + group + '" tabindex="0" role="button" aria-expanded="false"><span class="site-topnav-icon">' + icon + '</span><span>' + label + '</span><span class="site-topnav-arrow">▾</span><div class="site-topnav-dropdown">';
    items.forEach(function (item, index) {
      if (item[0] === "__divider__") {
        html += '<div class="site-topnav-divider"></div>';
      } else if (item[0] === "__section__") {
        html += '<div class="site-topnav-section">' + item[1] + '</div>';
      } else {
        var itemActive = currentKey === item[0] ? " active" : "";
        html += '<a class="' + itemActive.trim() + '" data-page="' + item[0] + '" href="' + page(item[0]) + '">' + item[1] + '</a>';
      }
    });
    html += '</div></div>';
    return html;
  }

  var menu = '';
  menu += link("index.html", "首页", "⌂", "home");
  menu += dropdown("业务场景", "▤", "scenes", [
    ["business-scenarios.html", "▤ 业务场景总览"],
    ["procurement-order-consolidation.html", "🔀 采购订单合并下推"],
    ["procurement-ap-management.html", "💰 供应商 AP 全生命周期"],
    ["outsourcing-cost-allocation.html", "🧩 委外成本分摊"],
    ["ior-bom.html", "🧱 IOR BOM 学习"],
  ]);
  menu += dropdown("ERP", "📦", "erp", [
    ["erp-center.html", "ERP 项目实施中心"],
    ["erp-procurement.html", "采购管理模块主页"],
    ["erp-procurement-detail.html", "采购业务详情"],
    ["erp-procurement-analysis.html", "采购数据分析"],
    ["erp-procurement-solution.html", "采购管理方案"],
    ["erp-procurement-warehouse.html", "采购与仓储"],
    ["erp-finance.html", "财务业务场景"],
    ["erp-finance-flow.html", "财务流程"],
  ]);
  menu += dropdown("PLM", "🔧", "plm", [
    ["plm-center.html", "PLM 项目实施中心"],
    ["plm-requirements.html", "33 条需求清单"],
    ["plm-business-flow.html", "研发六线业务流程"],
    ["plm-product-matrix.html", "产品矩阵"],
    ["plm-org-plm.html", "部门与 PLM 关联"],
    ["plm-kickoff.html", "项目启动会"],
    ["plm-kickoff_before_restructure.html", "项目启动会旧版"],
  ]);
  menu += dropdown("HR / EHR", "👥", "hr", [
    ["ehr-center.html", "EHR 系统中心"],
    ["hr-system-process.html", "HR 流程排查"],
    ["hr-system-policy.html", "HR 制度政策"],
    ["hr-requirement-template.html", "HR 需求模板"],
    ["italent-recruit-manual.html", "iTalent 招聘手册"],
  ]);
  menu += dropdown("IT 与公司", "💻", "it", [
    ["it-panorama.html", "IT 全景"],
    ["company-informatization.html", "企业信息化全景"],
    ["company-intro.html", "公司背景与产品"],
    ["management-reform.html", "管理变革中心"],
    ["reform-material.html", "物料管理模式转型"],
  ]);
  menu += dropdown("投资学习", "📈", "invest", [
    ["invest.html", "投资中心"],
    ["invest-market-cap.html", "市值金字塔"],
    ["invest-pe-valuation.html", "PE 估值实战"],
  ]);
  menu += dropdown("知识文件", "🗂️", "files", [
    ["key-files-overview.html", "关键文件总览"],
    ["key-files-manager.html", "关键文件管理"],
    ["keyfiles-pages/index.html", "关键文件目录"],
    ["life-hub.html", "生活知识架构"],
  ]);
  menu += link("site-map.html", "全站地图", "▦", "map");

  document.querySelectorAll(".topnav, .site-topnav").forEach(function (node) { node.remove(); });

  var nav = document.createElement("nav");
  nav.className = "site-topnav";
  nav.setAttribute("aria-label", "全站统一导航");
  nav.innerHTML = '<a class="site-topnav-brand" href="' + page("index.html") + '"><span class="site-topnav-logo">●</span><span>杰德瑞恩J · 信息化驾驶舱</span></a><div class="site-topnav-menu">' + menu + '</div><span class="site-topnav-note">全站统一导航</span>';
  document.body.insertBefore(nav, document.body.firstChild);

  var cssHref = page("shared-topnav.css");
  if (!document.querySelector('link[data-site-topnav-css="true"]')) {
    var css = document.createElement("link");
    css.rel = "stylesheet";
    css.href = cssHref;
    css.setAttribute("data-site-topnav-css", "true");
    document.head.appendChild(css);
  }

  nav.querySelectorAll(".has-dropdown").forEach(function (item) {
    item.addEventListener("click", function (event) {
      if (event.target.closest("a")) return;
      var expanded = item.getAttribute("aria-expanded") === "true";
      nav.querySelectorAll(".has-dropdown").forEach(function (other) { other.setAttribute("aria-expanded", "false"); });
      item.setAttribute("aria-expanded", String(!expanded));
    });
    item.addEventListener("keydown", function (event) {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        item.click();
      }
    });
  });

  document.addEventListener("click", function (event) {
    if (!event.target.closest(".site-topnav")) {
      nav.querySelectorAll(".has-dropdown").forEach(function (item) { item.setAttribute("aria-expanded", "false"); });
    }
  });
})();
