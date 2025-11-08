// JSX script to trigger a Photoshop action
// This script opens the PSD and runs a specified action

// Configuration
var psdPath = "C:\\Users\\dusosl\\Dropbox\\Youtube\\Patreon6.psd";
var csvPath = "c:\\git\\subscriber-list\\data\\levels.csv";
var actionName = "UpdatePatreon";  // Name of your action
var actionSet = "Default Actions"; // Action set name (change if needed)

try {
    // Open the PSD file
    var psdFile = new File(psdPath);
    if (!psdFile.exists) {
        alert("Error: PSD file not found at " + psdPath);
    } else {
        // Open the document
        var doc = app.open(psdFile);
        
        // Try to run the action
        try {
            app.doAction(actionName, actionSet);
            alert("Success! Action '" + actionName + "' completed.");
        } catch (e) {
            alert("Error running action '" + actionName + "':\n" + e.message + 
                  "\n\nMake sure you have created an action named '" + actionName + 
                  "' in the '" + actionSet + "' action set.\n\n" +
                  "To create the action:\n" +
                  "1. Window > Actions\n" +
                  "2. Create new action named 'UpdatePatreon'\n" +
                  "3. Record: Image > Variables > Data Sets > Import\n" +
                  "4. Record: File > Export > Save for Web\n" +
                  "5. Stop recording");
        }
    }
} catch (e) {
    alert("Error: " + e.message);
}
