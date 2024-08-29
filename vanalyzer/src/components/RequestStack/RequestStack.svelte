<script>
  import { Button } from "flowbite-svelte";
  import { requestStack, requestIndex } from "../../store/store";

  function processStatusMask(statusMaskDict) {
    const statusMaskBits = Object.keys(statusMaskDict)
      .reverse()
      .map((key) => (statusMaskDict[key] ? "1" : "0"))
      .join("");
    const statusMaskInt = parseInt(statusMaskBits, 2); // Convert binary string to integer

    // Convert the integer to a 2-byte hex string (e.g., 0x003F)
    const statusMaskHex = statusMaskInt
      .toString(16)
      .padStart(2, "0")
      .toUpperCase();

    return `0x${statusMaskHex}`;
  }
</script>

<div class="flex flex-col gap-4">
  {#each $requestStack as request, index}
    <Button
      color="alternative"
      on:click={() => {
        requestIndex.set(index);
        console.log(request);
      }}
    >
      {#each Object.entries(request) as [key, value], i (key)}
        <span>
          {key}:
          {#if key === "Status Mask"}
            {processStatusMask(value)}
          {:else}
            {value}
          {/if}
        </span>
        {#if i < Object.entries(request).length - 1}
          <div class="mx-2">|</div>
        {/if}
      {/each}
    </Button>
  {/each}
</div>
