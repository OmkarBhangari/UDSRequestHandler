<script>
  // @ts-nocheck

  import { Label, Select, Button, Input } from "flowbite-svelte";
  import { config } from "./constants";
  import { onMount } from "svelte";

  let selectedInterface = "pcan"; // Default to PCAN
  let selectedChannel;
  let selectedBaudrate;
  let selectedMessageType;
  let txId = "";
  let rxId = "";

  const interfaceOptions = [
    { value: "pcan", name: "PCAN" },
    { value: "vector", name: "Vector" }
  ];

  function handleUpdate() {
    console.log("Selected Interface:", selectedInterface);
    console.log("Selected Channel:", selectedChannel);
    console.log("Selected Baudrate:", selectedBaudrate);
    console.log("Selected Message Type:", selectedMessageType);
    console.log("Tx ID:", txId);
    console.log("Rx ID:", rxId);

    const updated_config = {
      "interface": selectedInterface,
      "channel": selectedChannel,
      "baud_rate": selectedBaudrate,
      "message_type": selectedMessageType,
      "tx_id": txId,
      "rx_id": rxId,
    };

    pywebview.api.update_config(updated_config);
  }

  function init(configData) {
    configData = JSON.parse(configData);
    selectedInterface = configData.interface || selectedInterface;
    selectedChannel = configData.channel || selectedChannel;
    selectedBaudrate = configData.baudrate || selectedBaudrate;
    selectedMessageType = configData.messageType || selectedMessageType;
    txId = configData.txId || txId;
    rxId = configData.rxId || rxId;
  }

  async function pollForConfig() {
    try {
      if (window.pywebview && window.pywebview.api) {
        const configData = await pywebview.api.get_config();
        init(JSON.parse(configData));
      } else {
        setTimeout(pollForConfig, 500);
      }
    } catch (error) {
      console.error("Error fetching config:", error);
      setTimeout(pollForConfig, 1000);
    }
  }

  onMount(() => {
    pollForConfig();
  });
</script>

<div class="flex items-end gap-8">
  <Label class="flex-1">
    Select Interface
    <Select class="my-2" items={interfaceOptions} bind:value={selectedInterface} />
  </Label>

  {#if selectedInterface === "pcan"}
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
  {/if}

  {#if selectedInterface === "vector"}
    <Label class="flex-1">
      Select Channel
      <Select class="my-2" items={config.vectorChannel} bind:value={selectedChannel} />
    </Label>

    <Label class="flex-1">
      Select Baudrate
      <Select class="my-2" items={config.vectorBaudrate} bind:value={selectedBaudrate} />
    </Label>
  {/if}

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