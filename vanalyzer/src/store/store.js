// @ts-nocheck
import { writable } from "svelte/store"

export const requestStack = writable([])
export const requestIndex = writable()
export const outputStack = writable([])
export const terminalStack = writable([])

window.outputStack = outputStack;