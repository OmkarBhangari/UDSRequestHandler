<script>
  //@ts-nocheck
  import { Button } from "flowbite-svelte";
  import ConfigBar from "./components/ConfigBar/ConfigBar.svelte";
  import Terminal from "./components/Terminal/Terminal.svelte";
  import RequestStack from "./components/RequestStack/RequestStack.svelte";
  import CreateRequestPannel from "./components/CreateRequestPannel/CreateRequestPannel.svelte";
  import OutputPannel from "./components/OutputPannel/OutputPannel.svelte";
  import { terminalHeight } from "./components/Terminal/constants";
  import { requestStack, outputStack, terminalStack } from "./store/store";

  let sessionActive = false;

  async function toggleSession() {
    pywebview.api.start_session();
    sessionActive = !sessionActive;
  }

  async function exportLog() {
    pywebview.api.exportLog($terminalStack, $requestStack, $outputStack)
    // let terminalContent = "";
    // for(let i=0; i<$terminalStack.length; i++) {
    //   const type = $terminalStack[i][0]
    //   const frame = $terminalStack[i][1]
    //   terminalContent += type == 'transmitted' ? 'tx' : 'rx';
    //   terminalContent += " " + frame + '\n';
    //   console.log(terminalContent)
    // }
    // const filename = "Hello.txt";
    // const result = await pywebview.api.save_file(terminalContent, filename);
  }
</script>

<div
  class={`grid grid-rows-[min-content, min-content,min-content,auto] grid-cols-[1fr,1fr] gap-4 p-4 mb-64`}
>
  <Button class="col-span-2 w-full" on:click={exportLog}>Export</Button>
  <!-- ConfigBar -->
  <div class="col-span-2 bg-gray-200 p-4 rounded-md">
    <ConfigBar />
  </div>

  <Button on:click={toggleSession} class="col-span-2"
    >{sessionActive ? "Stop Session" : "Start Session"}</Button
  >

  {#if sessionActive}
    <!-- RequestPanel -->
    <div class="col-span-1 bg-gray-100 p-4 rounded-md">
      <CreateRequestPannel />
    </div>

    <!-- RequestStack -->
    <div class="col-span-1 bg-gray-100 p-4 rounded-md">
      <RequestStack />
    </div>

    <!-- OutputPanel -->
    <div class="col-span-2 bg-gray-100 p-4 rounded-md">
      <OutputPannel />
    </div>
  {:else}
    <div class="h-max"></div>
  {/if}
</div>

<!-- Terminal (fixed at the bottom) -->
<div class="fixed bottom-0 bg-gray-300 p-4 w-full">
  <Terminal />
</div>
