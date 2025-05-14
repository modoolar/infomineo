odoo.define("infomineo_planning.GanttRow", function (require) {
    const GanttRow = require("web_gantt.GanttRow");

    GanttRow.include({
        _setResizable: function ($pill) {
            var parented_parent = this.getParent().getParent();

            if (parented_parent.modelName !== "planning.slot") {
                return this._super.apply(this, arguments);
            }

            var self = this;
            var pill = _.findWhere(self.pills, {id: $pill.data("id")});

            pill.disableStopResize = true;

            return this._super.apply(this, arguments);
        },
        _setDraggable: function ($pill) {
            var parented_parent = this.getParent().getParent();

            if (parented_parent.modelName !== "planning.slot") {
                return this._super.apply(this, arguments);
            }

            if ($pill.hasClass("ui-draggable-dragging")) {
                return;
            }

            var self = this;
            var pill = _.findWhere(this.pills, {id: $pill.data("id")});

            // DRAGGABLE
            if (this.options.canEdit && !pill.disableStartResize && !this.isGroup) {
                const resizeSnappingWidth = this._getResizeSnappingWidth();

                if ($pill.draggable("instance")) {
                    return;
                }
                if (!this.$containment) {
                    this.$containment = $("#o_gantt_containment");
                }
                $pill.draggable({
                    containment: this.$containment,
                    start: function (event, ui) {
                        self.trigger_up("updating_pill_started");

                        const pillWidth = $pill[0].getBoundingClientRect().width;
                        ui.helper.css({width: pillWidth});
                        ui.helper.removeClass("position-relative");

                        // The following trigger up will sometimes add the class o_hidden on the $pill.
                        // This is why the pill's width is computed above.
                        self.trigger_up("start_dragging", {
                            $draggedPill: $pill,
                            $draggedPillClone: ui.helper,
                        });

                        self.$el.addClass("o_gantt_dragging");
                        $pill.popover("hide");
                        self.$(".o_gantt_pill").popover("disable");
                    },
                    drag: function (event, ui) {
                        if ($(event.target).hasClass("o_gantt_pill_editing")) {
                            // Kill draggable if pill opened its dialog
                            return false;
                        }
                        var diff = self._getDiff(resizeSnappingWidth, ui.position.left);
                        self._updateResizeBadge(ui.helper, diff, ui);

                        const pointObject = {x: event.pageX, y: event.pageY};
                        const options = {container: document.body};
                        const $el = $.nearest(
                            pointObject,
                            ".o_gantt_hoverable",
                            options
                        ).first();
                        if ($el.length) {
                            // Remove ui-drag-hover class from other rows
                            $(".o_gantt_hoverable").removeClass("ui-drag-hover");
                            $el.addClass("ui-drag-hover");
                        }
                    },
                    stop: function () {
                        self.trigger_up("updating_pill_stopped");
                        self.trigger_up("stop_dragging");

                        self.$(".ui-drag-hover").removeClass("ui-drag-hover");
                        self.$el.removeClass("o_gantt_dragging");
                        self.$(".o_gantt_pill").popover("enable").popover("dispose");
                    },
                    helper: "clone",
                });
            } else if (!$pill.hasClass("o_gantt_consolidated_pill")) {
                if ($pill.draggable("instance")) {
                    return;
                }
                if (!this.$lockIndicator) {
                    this.$lockIndicator = $('<div class="fa fa-lock"/>').css({
                        "z-index": 20,
                        position: "absolute",
                        top: "4px",
                        right: "4px",
                    });
                }
                $pill.draggable({
                    // Prevents the pill from moving but allows to send feedback
                    grid: [0, 0],
                    start: function () {
                        self.trigger_up("updating_pill_started");
                        self.trigger_up("start_no_dragging");
                        $pill.popover("hide");
                        self.$(".o_gantt_pill").popover("disable");
                        self.$lockIndicator.appendTo($pill);
                    },
                    drag: function (ev) {
                        if ($(ev.target).hasClass("o_gantt_pill_editing")) {
                            // Kill draggable if pill opened its dialog
                            return false;
                        }
                    },
                    stop: function () {
                        self.trigger_up("updating_pill_stopped");
                        self.trigger_up("stop_no_dragging");
                        self.$(".o_gantt_pill").popover("enable").popover("dispose");
                        self.$lockIndicator.detach();
                    },
                });
                $pill.addClass("o_fake_draggable");
            }
        },
    });
});
