<!-- CustomDropdown.svelte -->
<script>
    import { Button, Dropdown, DropdownItem } from "flowbite-svelte";

    export let buttonText = "Dropdown button";
    export let items = [];
    export let buttonId = "dropdownButton";

    let dropdownOpen = false;

    function handleItemClick(item) {
        dropdownOpen = false;
        if (item.onClick) item.onClick();
    }
</script>

<Button id={buttonId}>{buttonText}</Button>
<Dropdown bind:open={dropdownOpen} triggeredBy={`#${buttonId}`}>
    {#each items as item}
        <DropdownItem on:click={() => handleItemClick(item)}>{item.text}</DropdownItem>
    {/each}
</Dropdown>