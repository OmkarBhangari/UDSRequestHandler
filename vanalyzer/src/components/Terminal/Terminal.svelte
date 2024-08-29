<script>
  // @ts-nocheck

  import { terminalStack } from "../../store/store";
  import { terminalHeight } from "./constants";
  import Outgoing from "./Outgoing.svelte";
  import Incoming from "./Incoming.svelte";
  function updateTerminalStack(newFrame) {
    terminalStack.update((prevData) => [...prevData, newFrame]);
  }
  window.updateTerminalStack = updateTerminalStack;
  function getColor(type) {
    if (type == "transmitted") {
      return "text-blue-500";
    } else if (type == "received") {
      return "text-green-500";
    } else if (type == "error") {
      return "text-red-500";
    }
  }
</script>

Terminal \>
<div class="h-52 overflow-auto">
  {#each $terminalStack as frame, index}
    <div>
      {index}
      {#if frame[0] == "transmitted"}
        <Outgoing />
      {:else}
        <Incoming />
      {/if}
      <div class={`inline-block ${getColor(frame[0])}`}>
        {#each frame[1] as byte}
          <div class="inline-block mr-2">{byte}</div>
        {/each}
      </div>
    </div>
  {/each}
</div>
