# LoadBalancEX
Example of use with Docker
LoadBalancEX angei$ docker build -t myload .
LoadBalancEX angei$ docker run -p 8080:8080 -v $(pwd)/appj.py:/appj.py myload --script /appj.py 


Regarding performace: 
I used japronto as it should have high performance  https://github.com/squeaky-pl/japronto (they tested on AWS c4.2xlarge instance)
My tests on my laptop were (of course lower) 6 second for 100 tests(just hello)or 18 second for 1000 get “get” also for my tests I used external open API which increase it 40 second for 100 tests (external )

For simplifying I saved all data including stats to appj.log

