async function getTimezone() {
  try {
    const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
    const response = await axios.post("/get-timezone", { timezone });
    console.log("Timezone updated successfully:", response.data);
  } catch (error) {
    console.error("Error updating timezone:", error);
  }
}

getTimezone();