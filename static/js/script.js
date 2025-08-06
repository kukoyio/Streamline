const searchBar = document.querySelector(".search-input");
const searchIcon = document.querySelector(".search-icon");
const testOut = document.getElementById("output");

searchIcon.addEventListener("click", () => {
    sendArtistName(searchBar.value);
})

searchBar.addEventListener("keypress", (event) => {
    if (event.key === "Enter") {
    // Cancel the default action, if needed
    event.preventDefault();
    // Trigger the button element with a click
    searchIcon.click();
    //testOut.textContent = searchBar.value;
    sendArtistName(searchBar.value);
  }
});

function sendArtistName(value){
    
}