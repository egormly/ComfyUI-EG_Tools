// ComfyUI-EG_Tools/web/dynamic_inputs.js
// Generic dynamic inputs for all Smart Switches

import { app } from "/scripts/app.js";

const egToolsDynamicInputs = {
    name: "EG.Tools.DynamicInputs",

    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        // Only process nodes in the Switch category
        if (!nodeData.category?.startsWith("EG Tools/Switch")) {
            return;
        }

        // Configuration constants
        const MAX_INPUTS = 8;
        const MIN_VISIBLE = 2;
        
        // Helper function to safely extract input type
        function getInputType(nodeData) {
            try {
                // Check if optional inputs exist and have input_1
                if (!nodeData.input?.optional?.input_1) {
                    console.warn(`[EG_Tools] No optional inputs found for ${nodeData.name}`);
                    return null;
                }
                
                // The type is the first element of the array, e.g., ["INT", { ... }]
                const inputType = nodeData.input.optional.input_1[0];
                
                if (!inputType) {
                    console.warn(`[EG_Tools] Could not determine input type for ${nodeData.name}`);
                    return null;
                }
                
                return inputType;
            } catch (error) {
                console.error(`[EG_Tools] Error detecting input type for ${nodeData.name}:`, error);
                return null;
            }
        }

        // Detect the input type from the node definition
        const baseType = getInputType(nodeData);
        
        // If we couldn't determine the type, don't modify the node
        if (!baseType) {
            return;
        }

        // Helper function to safely remove inputs from node definition
        function removePredefinedInputs(nodeData, maxInputs) {
            try {
                if (!nodeData.input?.optional) {
                    return;
                }
                
                for (let i = 1; i <= maxInputs; i++) {
                    const inputName = `input_${i}`;
                    if (nodeData.input.optional[inputName]) {
                        delete nodeData.input.optional[inputName];
                    }
                }
            } catch (error) {
                console.error(`[EG_Tools] Error removing predefined inputs:`, error);
            }
        }

        // Helper function to find the highest connected input index
        function findMaxConnectedIndex(inputs) {
            let maxConnectedIndex = 0;
            
            if (!inputs) {
                return maxConnectedIndex;
            }
            
            try {
                for (const input of inputs) {
                    if (input.name?.startsWith("input_") && input.link != null) {
                        const parts = input.name.split("_");
                        if (parts.length >= 2) {
                            const idx = parseInt(parts[1], 10);
                            if (!isNaN(idx) && idx > maxConnectedIndex) {
                                maxConnectedIndex = idx;
                            }
                        }
                    }
                }
            } catch (error) {
                console.error(`[EG_Tools] Error finding max connected index:`, error);
            }
            
            return maxConnectedIndex;
        }

        // Helper function to add missing inputs
        function addMissingInputs(node, targetInputs, baseType) {
            try {
                for (let i = 1; i <= targetInputs; i++) {
                    const inputName = `input_${i}`;
                    if (!node.inputs.find((inp) => inp.name === inputName)) {
                        node.addInput(inputName, baseType);
                    }
                }
            } catch (error) {
                console.error(`[EG_Tools] Error adding missing inputs:`, error);
            }
        }

        // Helper function to remove extra unconnected inputs
        function removeExtraInputs(node, targetInputs) {
            try {
                if (!node.inputs) {
                    return;
                }
                
                // Iterate backwards to avoid index issues when removing
                for (let i = node.inputs.length - 1; i >= 0; i--) {
                    const input = node.inputs[i];
                    if (input?.name?.startsWith("input_")) {
                        const parts = input.name.split("_");
                        if (parts.length >= 2) {
                            const idx = parseInt(parts[1], 10);
                            // Remove if it's beyond our target and not connected
                            if (!isNaN(idx) && idx > targetInputs && input.link == null) {
                                node.removeInput(i);
                            }
                        }
                    }
                }
            } catch (error) {
                console.error(`[EG_Tools] Error removing extra inputs:`, error);
            }
        }

        // 1. Modify the definition to remove the pre-defined inputs
        removePredefinedInputs(nodeData, MAX_INPUTS);

        // 2. Hook 'onNodeCreated' to add the initial minimum inputs
        const onNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            const result = onNodeCreated?.apply(this, arguments);
            
            try {
                // Add the minimum visible inputs
                for (let i = 1; i <= MIN_VISIBLE; i++) {
                    this.addInput(`input_${i}`, baseType);
                }
            } catch (error) {
                console.error(`[EG_Tools] Error in onNodeCreated:`, error);
            }
            
            return result;
        };

        // 3. Hook 'onConnectionsChange' for dynamic add/remove logic
        const onConnectionsChange = nodeType.prototype.onConnectionsChange;
        nodeType.prototype.onConnectionsChange = function (
            type, index, connected, link_info
        ) {
            const result = onConnectionsChange?.apply(this, arguments);
            
            try {
                // Find the highest connected input index
                const maxConnectedIndex = findMaxConnectedIndex(this.inputs);
                
                // Calculate how many inputs we should show
                const targetInputs = Math.max(
                    MIN_VISIBLE,
                    Math.min(maxConnectedIndex + 1, MAX_INPUTS)
                );

                // Add any missing inputs
                addMissingInputs(this, targetInputs, baseType);
                
                // Remove any extra unconnected inputs
                removeExtraInputs(this, targetInputs);

                // Mark the canvas as dirty to trigger a redraw
                this.setDirtyCanvas(true, true);
            } catch (error) {
                console.error(`[EG_Tools] Error in onConnectionsChange:`, error);
            }
            
            return result;
        };
    },
};

app.registerExtension(egToolsDynamicInputs);