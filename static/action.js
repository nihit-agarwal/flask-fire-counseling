const resultElement = document.getElementById("debug");
//resultElement.innerHTML = "Hello, great World!"; // Sets the content of the element to the specified value



  // Get the radio button and select element references
  const oldIITRadio = document.querySelector('input[name="oldIIT"]');
  const collegeSelect1 = document.getElementById('college1');
  const collegeSelect2 = document.getElementById('college2');
  const collegeSelect3 = document.getElementById('college3');
  const collegeSelect4 = document.getElementById('college4');
  const collegeSelect5 = document.getElementById('college5');
  //resultElement.innerHTML = collegeSelect1.value

  // Add an event listener to the radio button
  oldIITRadio.addEventListener('change', function() {
    // Get the selected radio button value
    const oldIITValue = this.value;

    // Update the selected option based on the radio button value
    if (oldIITValue === 'Y') {
      // Set the selected option to the desired value for 'Preferred' selection
      collegeSelect1.value = '102'; // Update with the desired value
      collegeSelect2.value = '104';
      collegeSelect3.value = '110';
      collegeSelect4.value = '109';
      collegeSelect5.value = '106';
    } else {
      // Set the selected option to the desired value for 'Don't Care' selection
      collegeSelect1.value = '0'; // Update with the desired value
      collegeSelect2.value = '0';
      collegeSelect3.value = '0';
      collegeSelect4.value = '0';
      collegeSelect5.value = '0';
    }
  });

