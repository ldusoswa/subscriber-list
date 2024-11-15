import ac
import acsys

def acMain(ac_version):
    # Create an app window
    app_window = ac.newApp("Driver Name Display")
    ac.setSize(app_window, 300, 100)

    # Set background transparency (0 = fully transparent, 1 = fully opaque)
    ac.setBackgroundOpacity(app_window, 0)  # Make the background fully transparent

    # Label to display the driver's name
    global driver_label
    driver_label = ac.addLabel(app_window, "Loading driver name...")

    # Style the text
    ac.setFontSize(driver_label, 32)  # Larger font size for better visibility
    ac.setFontAlignment(driver_label, "center")  # Center the text
    ac.setPosition(driver_label, 150, 40)  # Centered position in the window
    ac.setFontColor(driver_label, 1, 1, 1, 1)  # White text (RGBA format)

    return "Driver Name Display"

def acUpdate(delta_t):
    # Get the current driver's name using the API
    driver_name = ac.getDriverName(0)  # 0 is the index of the player

    # Update the label to display the driver's name
    ac.setText(driver_label, f"Driver: {driver_name}")
