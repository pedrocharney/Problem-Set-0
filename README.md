# harvardCS50x Final Project

[![IMAGE ALT TEXT HERE](https://img.youtube.com/vi/QJqorLvhCNI/0.jpg)](https://www.youtube.com/watch?v=QJqorLvhCNI)

# Registering new users (register.html)
I made a point of implementing a series of validations with java script that allow the user to receive real-time feedback on any possible problem with the registration, even before submitting it. The experience uses colors and alerts to ensure the visibility of information, always seeking to maximize the experience the user would have during registration.

# Dashboard (index.html)
The most difficult part of the project, on this page the user can access the list of events that they have already signed up to support, and also the list of events that are available for them to participate in according to the availability settings made in the Time Configuration tab ( timeconfig.html)

In this dash the user can also unsubscribe from the event, and when he or she does so, they are confronted with a modal that asks for confirmation that this is indeed the action the user wants to perform. This was more work than simply a button because I had to use java script, but as it is an action that removes something, I made a point of forcing the user to confirm the action.

The general idea here was to concentrate on the main information, which is first the events in which he/she confirmed participation, and of course after that the list of available events. Promoting greater engagement. Along with the available events, the user can also access the event details, to discover more details about the event, as well as other volunteers who confirmed their participation

# Time Configuration (timeconfig.html)
In this tab, the user has the opportunity to see details related to their own registration, as well as configure the days of the week that they are available to support.

Here the user can also register an exception day, being able to assign it an appointment, this way events that are scheduled for the exception day will not be displayed as available for the user to volunteer. This is super important because it guarantees that the user will not be disturbed by events that they will not be able to participate in, even generating possible frustration for other people who had confirmed their presence at the event.

# Events (event.html)
In this tab, the user can register a new event, as well as check all events that have already been created, being able to access their details or even delete them.

All events have a date to occur, a start time and an end time.

Let's say it was the easiest part to develop, but also one of the most difficult conceptually, because it was from there that I started the project.

# Event Detail (eventdetail.html)
Here the user sees the details of the events, and also the list of people who volunteered to participate in them.
If the user unsubscribes from the event, it continues to appear on the screen, but now as unconfirmed.

Note that this url is not available directly in the menu, but its access depends on the "?event" parameter which receives an ID to be accessed successfully.

Doing this project as a whole was much more complicated than I imagined, in total 6 different database tables were used. An additional complicating factor is the fact that as we are talking about events, we have to deal with date and time, days of the week and so on.

# TechStack 
The technology stack was HTML, CSS, Java Script, Python, Flask and SQL3 as the database.
