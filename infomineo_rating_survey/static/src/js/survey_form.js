odoo.define("infomineo_rating_survey.form", function (require) {
    var SurveyFormWidget = require("survey.form");

    SurveyFormWidget.include({
        _submitForm: function (options) {
            if (this.options.ratingToken === undefined) {
                this._super.apply(this, arguments);
            } else {
                this._submitRatingSurveyForm(options);
            }
        },

        _submitRatingSurveyForm: function (options) {
            var self = this;
            var params = {};
            if (options.previousPageId) {
                params.previous_page_id = options.previousPageId;
            }
            var route = "/rating/survey/submit";

            if (this.options.isStartScreen) {
                route = "/survey/begin";
                // Hide survey title in 'page_per_question' layout: it takes too much space
                if (this.options.questionsLayout === "page_per_question") {
                    this.$(".o_survey_main_title").fadeOut(400);
                }
            } else {
                var $form = this.$("form");
                var formData = new FormData($form[0]);

                if (!options.skipValidation) {
                    // Validation pre submit
                    if (!this._validateForm($form, formData)) {
                        return;
                    }
                }

                this._prepareSubmitValues(formData, params);
            }

            // Prevent user from submitting more times using enter key
            this.preventEnterSubmit = true;

            if (this.options.sessionInProgress) {
                // Reset the fadeInOutDelay when attendee is submitting form
                this.fadeInOutDelay = 400;
                // Prevent user from clicking on matrix options when form is submitted
                this.readonly = true;
            }

            var submitPromise = self._rpc({
                route: _.str.sprintf(
                    "%s/%s/%s/%s",
                    route,
                    this.options.ratingToken,
                    self.options.surveyToken,
                    self.options.answerToken
                ),
                params: params,
            });

            this._nextScreen(submitPromise, options);
        },
    });
});
