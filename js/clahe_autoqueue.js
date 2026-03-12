import { app } from "../../scripts/app.js";

const WEIGHT_DEFAULTS = {
    red_weight: 0.15,
    green_weight: 0.65,
    blue_weight: 0.20,
};

app.registerExtension({
    name: "clahe_preprocess.autoqueue",

    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name !== "CLAHEPreprocess") return;

        const origOnCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            origOnCreated?.apply(this, arguments);

            const node = this;
            let debounceTimer = null;
            const DEBOUNCE_MS = 500;

            // Wrap each widget's callback to auto-queue on change
            for (const widget of node.widgets || []) {
                const origCallback = widget.callback;
                widget.callback = (...args) => {
                    origCallback?.apply(widget, args);

                    clearTimeout(debounceTimer);
                    debounceTimer = setTimeout(() => {
                        app.queuePrompt(0);
                    }, DEBOUNCE_MS);
                };
            }

            // Add reset button for channel weights
            node.addWidget("button", "Reset Weights", null, () => {
                for (const [name, defaultVal] of Object.entries(WEIGHT_DEFAULTS)) {
                    const widget = node.widgets.find(w => w.name === name);
                    if (widget) {
                        widget.value = defaultVal;
                    }
                }
                clearTimeout(debounceTimer);
                debounceTimer = setTimeout(() => {
                    app.queuePrompt(0);
                }, DEBOUNCE_MS);
            });
        };
    },
});
