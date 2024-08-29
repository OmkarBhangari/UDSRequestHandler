<script>
  // @ts-nocheck

  import { outputStack, requestIndex } from "../../store/store";

  function updateOutputStack(newOutput) {
    console.log("Output Stack: ", newOutput);
    outputStack.update((prevOutput) => [...prevOutput, newOutput]);
    console.log($outputStack);
  }

  window.updateOutputStack = updateOutputStack;

  // Helper function to get the display value
  let displayValue = ""

  $: {
    const index = $requestIndex;
    if (index === undefined) {
      displayValue = $outputStack[$outputStack.length - 1] || "No data available";
    } else {
      displayValue = $outputStack[index];
    }
  }
</script>

<pre>{displayValue}</pre>
