
$("#classify-btn").on ("click", async function(evt) {
    
    evt.preventDefault();
    const url = `/textclassify`;
    try {
    
      const response = await axios.post(url, {
      });
      $('#classification-results').append(response)
    //   console.log("Goal progress updated", response.data);
    } catch (e) {
      console.error("Error updating the goal's progressL", e);
    }
})


/* <script>
  // $( document ).ready(function() {
  console.log("ready!");

  async function updateGoalProgress(goalId, dateStr, checkbox) {
    const url = `/update-goal-progress/${goalId}/${dateStr}`;
    try {
      const response = await axios.post(url, {
        completed: checkbox.checked,
      });
      console.log("Goal progress updated", response.data);
    } catch (e) {
      console.error("Error updating the goal's progressL", e);
    }
  }

  // Add click event listeners to checkboxes
  $('input[type="checkbox"]').click(function () {
    const goalId = $(this).data("goal-id");
    const dateStr = $(this).data("date");
    updateGoalProgress(goalId, dateStr, this);
  });

  // });
</script> */