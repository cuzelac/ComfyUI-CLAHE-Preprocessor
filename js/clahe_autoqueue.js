import { app } from "../../scripts/app.js";

app.registerExtension({
    name: "clahe_preprocess.autoqueue",

    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name !== "CLAHEPreprocess_TRELLIS") return;

        const origOnCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            origOnCreated?.apply(this, arguments);

            let debounceTimer = null;
            const DEBOUNCE_MS = 500;

            // Wrap each widget's callback to auto-queue on change
            for (const widget of this.widgets || []) {
                const origCallback = widget.callback;
                widget.callback = (...args) => {
                    origCallback?.apply(widget, args);

                    clearTimeout(debounceTimer);
                    debounceTimer = setTimeout(() => {
                        app.queuePrompt(0);
                    }, DEBOUNCE_MS);
                };
            }
        };
    },
});
