////////////////////////
// LOAD PAGE CONTENT ///
////////////////////////
document.addEventListener("DOMContentLoaded", function () {

	// Function to find the latest version based on date
	function getLatestVersion() {
		let latestVersion = null;
		let latestDate = new Date(0); // Start with a very old date
		for (const [version, date] of Object.entries(versions)) {
			if (date > latestDate) {
				latestDate = date;
				latestVersion = version;
			}
		}
		return latestVersion;
	}

	////// NOTE: version VARIABLE NEEDS TO BE DEFINED PREVIOUSLY (e.g. in html calling this JS) ///////

	// Check if the version exists in the list, otherwise load the latest version
	if (!version || !versions.hasOwnProperty(version)) {
		version = getLatestVersion(); // Load the latest version if none specified or invalid
	}

	// Create the dropdown and version note
	const versionNote = document.createElement("div");
	versionNote.id = "version-note";
	versionNote.innerHTML = `
		<span id="close-note">x</span>
		You are currently viewing version
		<select id="version-select">
			${Object.entries(versions).map(([ver, date]) => `
				<option value="${ver}" ${ver === version ? "selected" : ""}>
					${ver} (${date.toLocaleDateString()})
				</option>
			`).join('')}
		</select> of the <b><em>Machine Learning with SPIKE</em></b> workshop.
	`;

	// Append the version note at the top of the body
	document.body.prepend(versionNote);

	// Add event listener to the dropdown to load a different version
	document.getElementById("version-select").addEventListener("change", function (event) {
		const selectedVersion = event.target.value;
		window.top.location.href = `./index.html?version=${selectedVersion}`;
	});

	// Add event listener to the close "x" button to remove the message
	document.getElementById("close-note").addEventListener("click", function () {
		const note = document.getElementById("version-note");
		note.parentNode.removeChild(note); // Remove the version note from the DOM
	});
});
