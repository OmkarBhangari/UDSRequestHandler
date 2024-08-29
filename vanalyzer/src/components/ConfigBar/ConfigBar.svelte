<script>
  import { Label, Select, Button, Input } from "flowbite-svelte";
  import { config } from "./constants";

  let selectedChannel;
  let selectedBaudrate;
  let selectedMessageType;

  function handleUpdate() {
    console.log("Selected Channel:", selectedChannel);
    console.log("Selected Baudrate:", selectedBaudrate);
    console.log("Selected Message Type:", selectedMessageType);

    // Or display them in a div or paragraph below
    alert(
      `Channel: ${selectedChannel}\nBaudrate: ${selectedBaudrate}\nMessage Type: ${selectedMessageType}`,
    );
  }
</script>

<div class="flex items-end gap-8">
    <Label class="flex-1">
      Select Channel
      <Select class="my-2" items={config.channel} bind:value={selectedChannel} />
    </Label>

    <Label class="flex-1">
      Select Baudrate
      <Select class="my-2" items={config.baudrate} bind:value={selectedBaudrate} />
    </Label>

    <Label class="flex-1">
      Select Message Type
      <Select class="my-2" items={config.messageType} bind:value={selectedMessageType} />
    </Label>

    <Label class="flex-1">
      Rx ID
      <Input class="my-2"/>
    </Label>

    <Label class="flex-1">
      Tx ID
      <Input class="my-2"/>
    </Label>

  <Button on:click={handleUpdate} class="my-2" >Update</Button>
</div>
