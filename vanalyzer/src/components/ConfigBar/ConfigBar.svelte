<script>
  // @ts-nocheck

  import { Label, Select, Button, Input } from "flowbite-svelte";
  import { config } from "./constants";
  import { onMount } from "svelte";

  let selectedChannel;
  let selectedBaudrate;
  let selectedMessageType;
  let txId = "";
  let rxId = "";

  function handleUpdate() {
    console.log("Selected Channel:", selectedChannel);
    console.log("Selected Baudrate:", selectedBaudrate);
    console.log("Selected Message Type:", selectedMessageType);
    console.log("Tx ID:", txId);
    console.log("Rx ID:", rxId);

    const updated_config = {
      "channel": selectedChannel,
      "baud_rate": selectedBaudrate,
      "message_type": selectedMessageType,
      "tx_id": txId,
      "rx_id": rxId,
    };

    pywebview.api.update_config(updated_config);
  }

  // Initialize function to be called from the backend
  function init(configData) {
    configData = JSON.parse(configData);
    selectedChannel = configData.channel || selectedChannel;
    selectedBaudrate = configData.baudrate || selectedBaudrate;
    selectedMessageType = configData.messageType || selectedMessageType;
    txId = configData.txId || txId;
    rxId = configData.rxId || rxId;
  }

  // Polling function to check for the availability of get_config
  async function pollForConfig() {
    try {
      // Check if get_config is available
      if (window.pywebview && window.pywebview.api) {
        const configData = await pywebview.api.get_config();
        init(JSON.parse(configData));
      } else {
        // Retry after some time if get_config is not available
        setTimeout(pollForConfig, 500); // Poll every 500ms
      }
    } catch (error) {
      console.error("Error fetching config:", error);
      // Optionally, you can retry here or handle the error accordingly
      setTimeout(pollForConfig, 1000); // Retry after error
    }
  }

  onMount(() => {
    pollForConfig();
  });
</script>

<div class="flex items-end gap-8">
  <Label class="flex-1">
    Select Channel
    <Select class="my-2" items={config.channel} bind:value={selectedChannel} />
  </Label>

  <Label class="flex-1">
    Select Baudrate
    <Select
      class="my-2"
      items={config.baudrate}
      bind:value={selectedBaudrate}
    />
  </Label>

  <Label class="flex-1">
    Select Message Type
    <Select
      class="my-2"
      items={config.messageType}
      bind:value={selectedMessageType}
    />
  </Label>

  <Label class="flex-1">
    Rx ID
    <Input class="my-2" bind:value={rxId} />
  </Label>

  <Label class="flex-1">
    Tx ID
    <Input class="my-2" bind:value={txId} />
  </Label>

  <Button on:click={handleUpdate} class="my-2">Update</Button>
</div>
