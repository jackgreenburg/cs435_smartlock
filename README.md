# Smartlock: Abe Hoffman and Jack Greenburg

`middmarkit`, a student-led initiative to provide a better platform for items to be bought and sold on the Middlebury campus, was originally launched in the fall of 2020. The idea was simple–build an Instagram page to market for-sale items and facilitate the transactions. This required students to act as the middlemen between buyers and sellers. Scheduling the required pick-ups and drop-offs was inconvenient at best and impossible at worst, slowing down business significantly. While the mission of the company was positive, the experience was untenable.

This led us to believe that we could build a new system that would power the next iteration of `middmarkit`. Instead of spending hours facilitating item transfer, we wanted to build a frictionless asynchronous storage locker. The idea is similar to the Amazon Hub Locker; sellers are able to drop off items by unlocking the box, and buyers are able to collect their items in the same fashion. The core component of this box is the wifi-connected smart lock, which handles all locking interactions over WiFi and the MQTT protocol. Ultimately, by decreasing the burden of resale, we can reduce the number of items destined for the landfill, which if you’ve ever been to the recycling center at Middlebury, is a disturbing number of items.

This all boils down to the following goal of our project:

1. Develop a `wifi-connected smart lock` with integrated GPS tracking module and LED status display.
2. Connect the device to the `cloud` using the AWS IoT Core to allow an associated web app to open and close the lock.

---

## Research and Development

As we started to design the device, the two largest unknowns we had were how we would connect the device to the cloud, and how we would actually build the locking mechanism.

For connecting the device to the cloud, we found a great tutorial from AWS that described how to build an IoT thermal printer. While this tutorial provided a working understanding of the basics of connecting a device to the cloud, we weren’t able to use it for two reasons: it was outdated and was written in C++ (we planned to use micropython). But, this tutorial showed us that it was completely possible to achieve.

For the locking mechanism, we knew that we would need to have a component that when stress was applied to the system (for example someone trying to wrongfully break-in), the servo would not be load bearing. This would make sure that we could use a cheap servo to drive the locking mechanism without sacrificing the security of the locker. We found this YouTube tutorial for a 3d-printed pusher that we adapted for use as a lock in our project.

> With these two unknowns solved, we were off to the races to build an awesome smart lock.

---

### Methods

At a very high level, our project can be split up into the following categories:

![categories](https://user-images.githubusercontent.com/66453619/146081184-c6f6092a-97f6-4293-8b46-940129ec6272.png)

#### **Backend Infrastructure**

The backend infrastructure of our smart lock is reliant on AWS. We built a small, but easily extensible, API to manage the devices. At its core was the AWS IoT message broker that allowed the devices to communicate with the cloud and publish their current states. This broker also enabled our frontend interface to subscribe to the locks for real time updates.

![infrastructure](https://user-images.githubusercontent.com/66453619/146081705-ebc82099-8fb8-477f-8bbd-2c914adf95c3.png)

Following the flow from a user clicking the “unlock” button, the event loop was as follows:

1.  The client’s browser would make an XHR request to hit the API to unlock the selected device.
2.  The AWS API Gateway handles the incoming request and passes the request data to the Flask API running on AWS Lambda.
3.  This, in turn, would call the AWS IoT Core to publish a message to the /smartlock/unlock message topic.
4.  The AWS IoT core would push out this message over the MQTT protocol to the subscribed smart lock devices.
5.  The corresponding smart lock would then unlock and publish its updated state to the /smartlock/pub MQTT topic.
6.  At this point, the IoT core would do two things:

    a. Using an IoT Rule, it would parse the MQTT message and store this lock event in a DynamoDB table for logging and the API’s usage.

    b. Push out this message to the frontend which was subscribed via a websocket connection.

Boom. A user would be able to see (in real time) when the lock they selected was opening.

#### **Frontend**

![frontend](https://user-images.githubusercontent.com/66453619/146079672-8978348b-93c5-4d94-ba85-a206de40ae46.png)

We built a React app to enable an accessible and beautiful user experience. This allowed use of both desktop and mobile devices to unlock the box. We relied heavily on the Google Maps API to display the current locations of the smart locks.

#### **Device**

On device boot, the lock connects to WiFi and then subscribes to the AWS IoT message broker. Then, it executes its main program:

```python
import time

from board.log import logger

from board.mqtt import Client
from board.device_state import state
from board.hall import hall
from board.gps import gps

client = Client(
    topics=["/smartlock/unlock", "/smartlock/refresh"],
    state=state,
)

# Wrap the main loop in a try except block to restart the loop
# if an exception occurs. Probably bad practice, but not a bad idea.

while True:
    try:
      gps.update_state(state)
      hall.update_state(state=state, client=client)

      # Update the display
      logger(str(state))
      client.check_for_message()
      time.sleep(0.5)

    except Exception as e:
      print(e)
```

So what’s going on here? Each device maintains its own state that contains:

> **id**: the device id
>
> **now**: the current epoch timestamp driven by the real-time clock
>
> **lat**: the current latitude provided by the GPS
>
> **lng**: the current longitude provided by the GPS
>
> **locked**: the current lock state
>
> **last_closed**: the last epoch timestamp the box was closed
>
> **open**: the current box state

In each loop:

1. The device grabs the latest epoch timestamp, latitude, and longitude from the GPS device.

2. The device updates the current box state (open or closed) and lock state (locked or unlocked)

3. The device displays this information on its OLED display.

4. Finally, the device checks for a message from the AWS IoT message broker, if there is a pending message, it will execute a callback depending on the topic. For example, if the device receives a message on the `/smartlock/refresh` topic and the id in the message matches the smart lock's own id, it will publish the latest state to the `/smartlock/pub` MQTT topic.

---

### Bill of Materials

| Item                                       | Supplier                                                                                         | Unit Cost         |
| ------------------------------------------ | ------------------------------------------------------------------------------------------------ | ----------------- |
| Adafruit Huzzah ESP32 Feather              | [Adafruit](https://www.adafruit.com/product/3619)                                                | $21.95            |
| Ultimate GPS FeatherWing                   | [Adafruit](https://www.adafruit.com/product/3133)                                                | $24.95            |
| BONAI USB Power Bank External Battery Pack | [Amazon](https://www.amazon.com/Upgraded-BONAI-Flashlight-Compatible-Smartphones/dp/B07GFFGB2G/) | (w/ Prime) $12.39 |
| Male-Male Jumper Wires - 200mm x 40        | [Adafruit](https://www.adafruit.com/product/4482)                                                | $9.95             |
| FeatherWing OLED - 128x64 OLED Add-on      | [Adafruit](https://www.adafruit.com/product/4650)                                                | $14.95            |
| 3V Lithium Coin Cell Battery               | [Adafruit](http://www.adafruit.com/product/380)                                                  | $0.95             |
| FeatherWing Tripler Mini Kit               | [Adafruit](https://www.adafruit.com/product/3417)                                                | $8.50             |
| Magnetic contact switch (door sensor)      | [Adafruit](https://www.adafruit.com/product/375)                                                 | $3.95             |
| FEETECH FS90 Micro Servo\*                 | [Adafruit](https://www.adafruit.com/product/169)                                                 | $4.25             |
| Hinges STL Files                           | [Thingiverse](https://www.thingiverse.com/thing:4783423)                                         | Free              |
| Locking Mechanism STL Files\*\*            | [Thingiverse](https://www.thingiverse.com/thing:3170748)                                         | Free              |
|                                            |                                                                                                  | $101.84           |

### Result

Gifs (split into parts, one for each feature)
Failings (issues page, autolock because box jank (include gif of me holding lid down) )

---

### Accessibility

One of our focuses for this project was to ensure that interaction with the physical box itself was as limited, and therefore as painless, as possible. The only interaction required is lifting the lid, taking out an item or putting an item in, and then closing the lid. Interaction with the box can only be so simple because unlocking is handled by the web app and locking occurs automatically after the lid has been closed. There is a small LED screen that would be difficult to read for some users. However, it is not in any way necessary to utilize the device, as it merely displays information that is displayed on our web app.
As for the web app, it utilizes the built-in accessibility features of the Google Maps API. This means we benefit from all of the research and development that Google has put into ensuring a positive user experience for all. In theory, this means functionality for everyone on all devices. Unfortunately, the actual user experience with a screen reader is currently not polished.

---

### Ethical Implications

Most of the ethical implications of the device are neutral or positive. We have no ability to collect data on the users, so we avoid all issues of privacy. Use of the Google Maps API ensures an equal experience across all kinds of devices and in all locations. The biggest advantage is that the use of this device with `middmarkit` will make resale much more convenient, thereby encouraging reuse of products. Prolonging the lifespan of items will reduce how much gets thrown away, reducing waste.
There is still an ethical concern that we have. The use of this device through `middmarkit` would allow us to cut ourselves out of the process entirely. In theory this sounds like a logical progression in efficiency, but it also opens the door for some people to attempt illicit sales without us having the ability to know about it.

### Schedule

We originally planned to follow this schedule where we budgeted the most time to connect the device to the cloud.

![original_plan](https://user-images.githubusercontent.com/66453619/146081780-4a85d38f-1509-461e-bca9-0f1010e33daa.png)

However, due to the parts arriving at the beginning of week 4, we spent a lot of time building the web application, ensuring that the user experience would be awesome.

![actual_plan](https://user-images.githubusercontent.com/66453619/146081827-261e39ac-ff3a-4885-8d8e-5e833cc9d3f3.png)

---

### Issues

We, luckily, encountered only a few issues during the development of our project. The first was that despite the GPS claiming to be I2C compatible, we do not believe that this was possible. Therefore, we were forced to communicate with the device over UART. Since the libraries we tried to use to read the GPS data failed to work, we wrote our own basic NMEA sentence parser but saw that the device was claiming to be somewhere it wasn’t. We originally attributed this to the devices being indoors and failing to get an accurate satellite lock. However, the real issue was that the NMEA sentence provided the latitude and longitude in degrees and minutes rather than decimal. After a quick fix, the location was working awesome.
One of the other issues we encountered was we were unable to source an accurate way to determine the battery percentage. We believed this would be easy since the power bank had its own LED indicator, but we could not find the data we needed. Therefore, we decided to leave this feature out of our project.

Finally, it is worth noting that AWS went down the day of our demo. While this is highly unlikely, building our project on AWS was a risk that unfortunately bit us in the rear.

---

### Future work

If we had more time to work on this project, we would definitely want to do several things:

- Figure out how to monitor battery percentage (perhaps plotting the battery percentage over time with a multimeter and fitting a curve)
- Build a secure, full scale locker.
- Test it out with real users.

Ultimately, we were super stoked about our project and had a lot of fun locking and unlocking the device.

---

### References
Code references:
- https://docs.micropython.org
- https://www.adafruit.com/
- https://medium.com/serverlessguru/serverless-real-time-reactjs-app-aws-iot-mqtt-17d023954045
- https://forum.micropython.org/viewtopic.php?t=5166
- https://github.com/nemart69/sh1107-micropython
- http://freenmea.net/decoder
- Andrea Vaccari!

3D printed components:
- https://youtube.com/watch?v=2vAoOYF3m8U
- https://thingiverse.com/thing:4783423

