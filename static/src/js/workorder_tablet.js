// 定义模块 'mrp_workorder.TabletNoReload' 及其依赖项
odoo.define('mrp_workorder.TabletNoReload', function (require) {
    "use strict";

    // 导入所需模块
    var FormRenderer = require('web.FormRenderer');
    var FormView = require('web.FormView');
    var viewRegistry = require('web.view_registry');


    // 定义 TabletNoReloadRenderer 类，继承自 FormRenderer
    var TabletNoReloadRenderer = FormRenderer.extend({
        init: function () {
            // 调用父类的 init 方法
            this._super.apply(this, arguments);
            // 初始化 workorderViewer 变量
            this.workorderViewer = undefined;
        },


        // 重写 FormRenderer 的 _renderNode 方法
        _renderNode: function (node) {
            if (node.tag === 'button') {
                //console.log('node',node);
                //console.log('arguments',arguments);
                this.workorderViewer = this._super.apply(this, arguments);
                // 返回 workorderViewer
                return this.workorderViewer;
            } else {
                // 对于其他节点，调用父类的 _renderNode 方法
                return this._super.apply(this, arguments);
            }
        },
    });

    // 定义 TabletPDFViewer 类，继承自 FormView
    var TabletPDFViewer = FormView.extend({
        // 扩展 FormView 的默认配置对象
        config: _.extend({}, FormView.prototype.config, {
            Renderer: TabletNoReloadRenderer,  // 使用 TabletNoReloadRenderer 作为渲染器
        }),
    });

    // 将 TabletPDFViewer 类添加到视图注册表，键名为 'workorder_tablet_viewer'
    viewRegistry.add('workorder_tablet_viewer', TabletPDFViewer);



    // 导出对象
    return {
        TabletNoReloadRenderer: TabletNoReloadRenderer,
        TabletPDFViewer: TabletPDFViewer,
    };
});
