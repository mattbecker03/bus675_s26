# Lab 2 Reflection

In this lab, both containers ran on your laptop. In production, the preprocessor would run in the warehouse datacenter and the inference API would run in Congo's main datacenter.

**How would the architecture and your `docker run` commands differ if these containers were actually running in separate datacenters?**

Consider:
- How would the preprocessor find the inference API?
- What about the shared volumes?
- What new challenges would arise?


## Your Reflection Below

PUT YOUR REFLECTION HERE.
In this lab, both containers ran on the same laptop, so they could communicate through Docker using host.docker.internal and local mounted folders. The preprocessor was able to send images to the inference API because both services were on the same local machine. In a real production environment, the preprocessor would not use a local Docker address. Instead, it would use a real network address, such as an HTTPS URL or private database to reach the inference API.

For the shared volumes, local mounted folders would no longer work because the containers would be running in separate datacenters and would not share the same filesystem. The warehouse system would upload images to a shared storage, and the inference API would write results to a central database or log files. Some new challenges would include security, reliability, and keeping data synchronized across multiple machines.