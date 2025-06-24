// File: image_batch_utils/js/create_batch_node.js

import { app } from "/scripts/app.js";
import { api } from "/scripts/api.js";

app.registerExtension({
	name: "ImageBatchUtils.CreateImageBatch",

	async nodeCreated(node) {
		node.specialWidget = new ImageBatchEditor(node);
	},
});

class ImageBatchEditor {
	constructor(node) {
		this.node = node;
		this.imageData = [];
		this.selectedIndex = -1;
		this.isInitialized = false;

		this.widthWidget = node.widgets.find((w) => w.name === "width");
		this.heightWidget = node.widgets.find((w) => w.name === "height");
		this.batchSizeWidget = node.widgets.find((w) => w.name === "batch_size");
		this.dataWidget = node.widgets.find((w) => w.name === "image_data");
		this.dataWidget.type = "hidden";

		this.container = document.createElement("div");
		this.container.className = "image-batch-editor";

		this.grid = document.createElement("div");
		this.grid.className = "image-batch-grid";
		this.container.appendChild(this.grid);

		this.editorPanel = this.createEditorPanel();
		this.container.appendChild(this.editorPanel);

		node.addDOMWidget("editor", "app", this.container);

		this.bindEvents();
		setTimeout(() => this.updateAndRedraw(), 0);
	}

	createEditorPanel() {
		const panel = document.createElement("div");
		panel.className = "editor-panel";
		panel.style.display = "none";

		const colorGroup = document.createElement("div");
		colorGroup.className = "editor-row";
		colorGroup.innerHTML = `<span>Color:</span>`;
		this.colorInput = document.createElement("input");
		this.colorInput.type = "color";
		this.colorInput.value = "#000000";
		colorGroup.appendChild(this.colorInput);
		const setColorBtn = document.createElement("button");
		setColorBtn.innerText = "Set Color";
		setColorBtn.onclick = () => this.setColor();
		colorGroup.appendChild(setColorBtn);
		panel.appendChild(colorGroup);

		const fileGroup = document.createElement("div");
		fileGroup.className = "editor-row";
		this.fileInput = document.createElement("input");
		this.fileInput.type = "file";
		this.fileInput.accept = "image/jpeg,image/png,image/webp";
		this.fileInput.style.display = "none";
		const uploadBtn = document.createElement("button");
		uploadBtn.innerText = "Load Image...";
		uploadBtn.onclick = () => this.fileInput.click();
		this.fileInput.onchange = (e) => this.uploadFile(e.target.files[0]);
		fileGroup.appendChild(uploadBtn);
		fileGroup.appendChild(this.fileInput);
		panel.appendChild(fileGroup);

		return panel;
	}

	bindEvents() {
		this.widthWidget.callback = () => this.updateAndRedraw();
		this.heightWidget.callback = () => this.updateAndRedraw();
		this.batchSizeWidget.callback = () => this.updateAndRedraw();
	}

	updateAndRedraw() {
		if (!this.isInitialized) {
			try {
				const loadedData = JSON.parse(this.dataWidget.value);
				if (Array.isArray(loadedData)) {
					this.imageData = loadedData;
				}
			} catch (e) {
				// Ignore parse errors, will default to an empty array
			}
			this.isInitialized = true;
		}
		const batchSize = this.batchSizeWidget.value;

		if (this.imageData.length > batchSize) {
			this.imageData.length = batchSize;
		} else {
			while (this.imageData.length < batchSize) {
				this.imageData.push({ type: "color", value: "#000000" });
			}
		}

		this.dataWidget.value = JSON.stringify(this.imageData);

		this.drawGrid();
		this.drawEditor();
        this.node.onResize?.(this.node.size);
	}

	drawGrid() {
		this.grid.innerHTML = "";
		const width = this.widthWidget.value;
		const height = this.heightWidget.value;

		this.imageData.forEach((data, index) => {
			const cell = document.createElement("div");
			cell.className = "grid-cell";
			if (index === this.selectedIndex) {
				cell.classList.add("selected");
			}
			cell.onclick = () => this.selectImage(index);

			const canvas = document.createElement("canvas");
			const ctx = canvas.getContext("2d");
			canvas.width = 128;
			canvas.height = 128 * (height / width);

			if (data.type === "color") {
				ctx.fillStyle = data.value;
				ctx.fillRect(0, 0, canvas.width, canvas.height);
			} else if (data.type === "file") {
				const img = new Image();
				img.onload = () => {
					ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
				};
				img.src = api.apiURL(`/view?filename=${encodeURIComponent(data.value)}&type=input`);
			}

			const indexLabel = document.createElement("span");
			indexLabel.className = "grid-cell-index";
			indexLabel.innerText = index;

			cell.appendChild(canvas);
			cell.appendChild(indexLabel);
			this.grid.appendChild(cell);
		});
	}

	drawEditor() {
		if (this.selectedIndex !== -1) {
			this.editorPanel.style.display = "block";
			const currentData = this.imageData[this.selectedIndex];
			if (currentData.type === 'color') {
				this.colorInput.value = currentData.value;
			}
		} else {
			this.editorPanel.style.display = "none";
		}
	}

	selectImage(index) {
		this.selectedIndex = index;
		this.updateAndRedraw();
	}

	setColor() {
		if (this.selectedIndex === -1) return;
		this.imageData[this.selectedIndex] = { type: "color", value: this.colorInput.value };
		this.updateAndRedraw();
	}

	async uploadFile(file) {
		if (this.selectedIndex === -1 || !file) return;

		try {
			const formData = new FormData();
			formData.append("image", file);
			const response = await api.uploadImage(formData, true);
			if (response.name) {
				this.imageData[this.selectedIndex] = { type: "file", value: response.name };
				this.updateAndRedraw();
			}
		} catch (error) {
			console.error("Error uploading file:", error);
			alert("File upload failed. See console for details.");
		}
	}
}

const style = document.createElement('style');
style.innerHTML = `
.image-batch-editor {
    width: 100%;
}
.image-batch-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(48px, 1fr));
    gap: 0;
    margin-bottom: 10px;
}
.grid-cell {
    position: relative;
    cursor: pointer;
    border: 1px solid transparent;
}
.grid-cell canvas {
    width: 100%;
    height: auto;
    display: block;
}
.grid-cell.selected {
    border-color: var(--accent-color, #00A6ED);
}
.grid-cell-index {
	position: absolute;
	top: 2px;
	left: 2px;
	background: rgba(0,0,0,0.7);
	color: white;
	font-size: 10px;
	padding: 1px 3px;
	border-radius: 3px;
}
.editor-panel {
    display: flex;
    flex-direction: column;
    gap: 5px;
    padding: 5px;
    border: 1px solid var(--border-color, #444);
    border-radius: 4px;
}
.editor-panel .editor-row {
    display: flex;
    align-items: center;
    gap: 5px;
    margin-bottom: 5px;
}
.editor-panel button {
    padding: 2px 8px;
}
`;
document.head.appendChild(style);