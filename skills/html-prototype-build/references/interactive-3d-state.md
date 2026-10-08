# Interactive 3D state and gesture recipe

Use this reference when a single-file 3D prototype must be manipulated, not merely viewed.

## Build order

1. Define the logical model before the mesh model. Keep each selectable unit in a plain data record with stable identity, integer coordinates, orientation/sticker state, and the face or layer membership it currently occupies.
2. Render from that model. Do not make mesh transforms the source of truth. After a move, update the records, rebuild or rebind the affected presentation objects, and assert that the rendered stickers agree with the model.
3. Represent a turn as a command: axis, layer coordinate, direction, and quarter-turn count. Apply the command to the selected records with an exact 90-degree coordinate rotation, then rotate sticker normals/orientations with the same transform. Keep inverse turns as the same command with the sign reversed.
4. Animate the command separately from committing it. Put the affected meshes under a temporary pivot, animate the pivot to the target angle, then snap the logical state and mesh positions to exact grid values at completion. Never accumulate floating-point angles across moves.
5. Use one pointer-event pipeline for mouse and touch. Track `pointerId`, capture the pointer on start, and release it on end/cancel. Distinguish a scene drag from a layer gesture only after movement crosses a threshold: empty/background drag rotates the scene; a drag beginning on a selectable face can turn its layer; UI controls must stop propagation.
6. Expose a deterministic control path in addition to gestures. Buttons and keyboard commands make QA and accessibility possible even when face-drag direction is ambiguous. Provide reset, scramble, undo or inverse-turn controls when the model supports them.
7. Keep visual polish subordinate to interaction truth. Use bevels, seams, lighting, shadows, responsive layout, and reduced-motion handling, but do not add a control, label, or status readout unless it is connected to live state.
8. Verify both state and presentation. A successful animation or canvas render is not proof that the puzzle moved correctly. Test a move followed by its inverse, four identical quarter-turns returning to the original state, scramble/reset, and at least one pointer scene rotation and zoom gesture.

## Browser assertions

- Attach `console` and `pageerror` listeners before navigation.
- Assert the canvas or WebGL renderer exists and has nonzero dimensions.
- Assert the initial model has the expected unit count and sticker/color inventory.
- Invoke a deterministic face command, wait for animation completion, and compare a serialized model snapshot before and after.
- Invoke the inverse command and require an exact snapshot match with the initial state.
- Invoke the same quarter-turn four times and require an exact snapshot match with the initial state.
- Dispatch a pointer drag on the scene and require camera orientation or scene rotation to change.
- Dispatch wheel or pinch-equivalent input and require camera distance or zoom state to change.
- Test a narrow viewport and keyboard controls; check that focused buttons have visible focus and that reduced-motion mode does not prevent state updates.

## Common failure modes

- Do not infer puzzle state from CSS transforms or accumulated Euler angles; presentation transforms drift and cannot reliably answer whether a move was solved.
- Do not use the first pointer movement to decide the gesture mode; a tiny diagonal jitter makes layer turns and camera orbit fight each other. Use a movement threshold and commit the mode once.
- Do not rotate only the cubie position while leaving sticker orientation unchanged; side colors then become visually wrong after the first turn.
- Do not let a drag end outside the canvas lose the command; pointer capture is required for touch and fast mouse drags.
- Do not validate only button clicks; a polished interactive 3D artifact can pass static tests while its pointer path is dead.
- Do not claim full layer-drag interaction when only buttons or keyboard commands work. Report the implemented interaction scope precisely and list gesture extensions separately.
