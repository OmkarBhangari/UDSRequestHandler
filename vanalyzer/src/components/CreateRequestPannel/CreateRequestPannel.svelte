<script>
  // @ts-nocheck

  import { Label, Select, Checkbox, Input, Button } from "flowbite-svelte";
  import { data, hasStatusMask } from "./constants"; // Assuming the data object is in a separate file
  import { requestStack } from "../../store/store";


  let sid;
  let formData = {};

  $: selectedData = data.find((item) => item.request === sid)?.fields || [];

  // Initialize formData for checkboxes when selectedData changes
  $: {
    selectedData.forEach((field) => {
      if (field.type === "checkboxes" && !formData[field.name]) {
        formData[field.name] = {};
        field.options.forEach((option) => {
          if (!(option in formData[field.name])) {
            formData[field.name][option] = false;
          }
        });
      }
    });
  }

  function handleSubmit() {
    let result = { sid };
    selectedData.forEach((field) => {
      if (field.type === "select" || field.type === "text") {
        result[field.name] = formData[field.name];
      } else if (field.type === "checkboxes" && hasStatusMask.includes(formData['Sub Functions'])) {
        result[field.name] = formData[field.name]; // Store true/false values directly
      }
    });
    pywebview.api.send_request(result);
    console.log(result);
    requestStack.update((request) => [...request, result]);
    console.log($requestStack);
  }
</script>

<Label class="flex-1">
  Select SID
  <Select
    class="my-2"
    items={data.map((item) => {
      return { name: item.request, value: item.request };
    })}
    bind:value={sid}
  />
</Label>

{#if selectedData.length > 0}
  {#each selectedData as field}
    {#if field.type === "select"}
      <Label class="flex-1 mt-4">
        {field.name}
        <Select
          class="my-2"
          items={field.options.map((item) => {
            return { name: item, value: item };
          })}
          bind:value={formData[field.name]}
        />
      </Label>
    {:else if field.type === "checkboxes" && hasStatusMask.includes(formData['Sub Functions'])}
      <div class="grid grid-cols-[1fr,1fr] mt-4">
        {#each field.options as option}
          <Checkbox
            class="my-2"
            bind:checked={formData[field.name][option]}
          >
            {option}
          </Checkbox>
        {/each}
      </div>
    {:else if field.type === "text"}
      <Label class="block mb-2 mt-4">{field.name}</Label>
      <Input placeholder={field.name} bind:value={formData[field.name]} />
    {/if}
  {/each}
{/if}

<Button class="w-full my-4" on:click={handleSubmit}>Send Request</Button>
