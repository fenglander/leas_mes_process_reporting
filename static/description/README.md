
# Document Page

> The original text is in Chinese, and the text is machine translated.
<!-- TOC -->
* [Document Page](#document-page)
    * [Overview](#overview)
    * [Feature Introduction](#feature-introduction)
      * [User-Friendly Reporting Interface](#user-friendly-reporting-interface)
      * [Detailed Recording of Manufacturing Process](#detailed-recording-of-manufacturing-process)
      * [Support for Parallel Process](#support-for-parallel-process)
      * [Adjustable Processing Time and Quantity](#adjustable-processing-time-and-quantity)
    * [Installation Requirements](#installation-requirements)
    * [Development Plan](#development-plan)
    * [Bug Tracker](#bug-tracker)
    * [Contributors & Maintainers](#contributors--maintainers)
<!-- TOC -->

###  Overview
In the management of operation reporting, it is crucial to accurately record the start and end time of each 
operation, as well as the quantity processed at each station, in order to reflect the real production capacity.
Additionally, it is important to control the production process to ensure that products are manufactured 
according to the defined process. This ensures the accuracy and efficiency of the production process.



### Feature Introduction
#### User-Friendly Reporting Interface
Track by Code for Quick Work Order Navigation. Display only the information relevant to production floor personnel's concerns, with a simple operational layout.  
![](/Demo2.gif)  

worksheet  

![](/Demo3.gif)

#### Detailed Recording of Manufacturing Process
Record the start and completion times for each manufacturing operation, planned start quantity, and actual completion quantity. Adapt to pauses and exceptions within the Manufacturing module itself.  
![](/Demo1.gif)

#### Support for Parallel Process
The startable quantity for each operation is influenced by the completion quantity of the previous reporting point.  
Reporting points can be adjusted according to business needs to control critical operations.  
![](/Demo5.png)

#### Adjustable Processing Time and Quantity
After reporting is completed, you can make modifications to start time, completion time, start quantity, and completion quantity. These changes will automatically update the work order information and related processing records.  
![](/Demo4.gif)

> For cases of resuming work after a pause, the system will meticulously record relationships between multiple reporting entries. This aids in accurately tracking and visualizing changes within the workflow.  
> Completed work orders or records cannot have their quantities modified, but their processing time can be adjusted. This ensures the accuracy of production data while allowing adjustments to actual processing time.


### Installation Requirements
Before using this plugin, make sure you have installed and activated the Manufacturing module and Work Order functionality.  
![](/Demo6.png)


### Development Plan

- [x] Operation Process Reporting
- [ ] Production Quality Management
- [ ] Register Equipment Molds
- [ ] WorkOrder Serial Number
- [ ] Serial Number Reporting

### Bug Tracker
Bugs are tracked on [GitHub Issues](https://github.com/fenglander/leas_mes_process_reporting/issues)  
If you encounter an issue, please check here to see if your problem has already been reported.  
If you are the first to discover the issue, please help us resolve it by providing detailed information.

### Contributors & Maintainers

* Fung

