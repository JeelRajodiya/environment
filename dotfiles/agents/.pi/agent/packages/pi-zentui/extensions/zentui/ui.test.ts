import type { KeybindingsManager, Theme } from "@earendil-works/pi-coding-agent";
import { CombinedAutocompleteProvider, type EditorTheme, type TUI } from "@earendil-works/pi-tui";
import { describe, expect, it, vi } from "vitest";
import type { ZentuiConfig } from "./config";
import { createMinimalistViewportTui, PolishedEditor } from "./ui";

function createPolishedEditor(
	commands: ConstructorParameters<typeof CombinedAutocompleteProvider>[0],
) {
	const identity = (text: string) => text;
	const editorTheme: EditorTheme = {
		borderColor: identity,
		selectList: {
			selectedPrefix: identity,
			selectedText: identity,
			description: identity,
			scrollInfo: identity,
			noMatch: identity,
		},
	};
	const editor = new PolishedEditor(
		{ requestRender: vi.fn() } as unknown as TUI,
		editorTheme,
		{ matches: () => false } as unknown as KeybindingsManager,
		{} as Theme,
		() => ({ components: { editor: { enabled: true, style: "opencode" } } }) as ZentuiConfig,
		() => ({ modelLabel: "", providerLabel: "" }),
		() => undefined,
	);
	editor.setAutocompleteProvider(new CombinedAutocompleteProvider(commands, process.cwd()));
	return editor;
}

describe("PolishedEditor slash argument autocomplete", () => {
	it.each([
		["/agents variant", "agents", "variant ", "balanced-sol-review"],
		["/model gpt", "model", "gpt ", "gpt-6-luna"],
	])(
		"reopens argument suggestions after a space in %s",
		async (text, command, prefix, suggestion) => {
			const completions = vi.fn(async (_prefix: string) => [{ value: suggestion, label: suggestion }]);
			const editor = createPolishedEditor([{ name: command, getArgumentCompletions: completions }]);
			editor.setText(text);
			expect(editor.isShowingAutocomplete()).toBe(false);

			editor.handleInput(" ");
			await vi.waitFor(() => expect(editor.isShowingAutocomplete()).toBe(true));
			expect(completions).toHaveBeenCalledWith(prefix);

			const trigger = vi.spyOn(
				editor as unknown as { tryTriggerAutocomplete: () => void },
				"tryTriggerAutocomplete",
			);
			editor.handleInput(" ");
			expect(trigger).not.toHaveBeenCalled();
		},
	);

	it("does not trigger suggestions for ordinary prose", () => {
		const completions = vi.fn(async (_prefix: string) => [{ value: "variant", label: "variant" }]);
		const editor = createPolishedEditor([{ name: "agents", getArgumentCompletions: completions }]);
		editor.setText("ordinary prose");
		editor.handleInput(" ");
		expect(completions).not.toHaveBeenCalled();
		expect(editor.isShowingAutocomplete()).toBe(false);
		editor.setText("/");
		editor.handleInput(" ");
		expect(completions).not.toHaveBeenCalled();
	});
});

describe("createMinimalistViewportTui", () => {
	it("dynamically caps only the enabled minimalist editor and binds delegated members", () => {
		let rows = 33;
		const terminal = {
			get rows() {
				return rows;
			},
			readRows() {
				return this.rows;
			},
		};
		const tui = {
			terminal,
			readTerminal() {
				return this.terminal;
			},
		} as unknown as TUI;
		const editor = { enabled: true, style: "minimalist" };
		const config = { components: { editor } } as unknown as ZentuiConfig;
		const proxy = createMinimalistViewportTui(tui, () => config);

		for (const [terminalRows, reportedRows] of [
			[33, 33],
			[34, 34],
			[36, 36],
			[37, 36],
			[100, 36],
		] as const) {
			rows = terminalRows;
			expect(proxy.terminal.rows).toBe(reportedRows);
		}
		expect((proxy.terminal as typeof terminal).readRows()).toBe(100);
		expect(proxy.readTerminal()).toBe(terminal);
		editor.style = "opencode";
		expect(proxy.terminal.rows).toBe(100);
		editor.style = "minimalist";
		editor.enabled = false;
		expect(proxy.terminal.rows).toBe(100);
	});
});
