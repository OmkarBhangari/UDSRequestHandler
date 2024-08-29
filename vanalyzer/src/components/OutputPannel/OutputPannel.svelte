<script>
  // @ts-nocheck

  import { outputStack, requestIndex } from "../../store/store";
  function updateOutputStack(newOutput) {
    console.log("Output Stack: ", newOutput)
    outputStack.update((prevOutput) => [...prevOutput, newOutput]);
    console.log($outputStack)
  }
  window.updateOutputStack = updateOutputStack;
</script>

<pre>{$outputStack[$requestIndex]}</pre>
