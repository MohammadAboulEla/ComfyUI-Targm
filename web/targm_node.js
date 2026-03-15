import { app } from "../../../scripts/app.js";

const showToast = (severity, summary, detail) => {
  app.extensionManager.toast.add({ severity, summary, detail, life: 2000 });
};

app.registerExtension({
  name: "base.Targm",
  async nodeCreated(node) {
    const allow_auto_coloring = false;
    if (node.comfyClass !== "TARGM") {
      return;
    }
    if (allow_auto_coloring) {
      node.color = LGraphCanvas.node_colors.blue.color;
      node.bgcolor = LGraphCanvas.node_colors.cyan.bgcolor;
    }
  },
});
