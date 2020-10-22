evothings.aws = evothings.aws || {}

/**
 * Initialize AWS EC2.
 * @param config Object with configuration parameters,
 * see file aws-config.js
 */
evothings.aws.initEC2 = function (config) {
	evothings.aws.ec2 = new AWS.EC2(config)
}

evothings.aws.initEBS = function (config) {
	evothings.aws.ebs = new AWS.EBS()
}

// /**
//  * Update a sensor.
//  * @param sensorid ID of the sensor
//  * @param value Value of the sensor
//  * @param success Success callback: success()
//  * @param error Error callback: success(err)
//  */
// evothings.aws.update = function (sensorid, value, success, error) {
// 	var params = {
// 		Payload: JSON.stringify({
// 			operation: 'update',
// 			sensorid: sensorid,
// 			value: value
// 		})
// 	}
// 	evothings.aws.ec2.invoke(
// 		params,
// 		function (err, data) {
// 			if (err) {
// 				error && error(err)
// 			}
// 			else {
// 				success && success(data)
// 			}
// 		}
// 	)
// }

evothings.aws.update = function (value, success, error) {
	var params = {
		InstanceIds: [
			"i-056d98a0bc013fbbc"
		],
		AdditionalInfo: value
	};
	evothings.aws.ec2.startInstances(params, function (err, data) {
		if (err) {
			console.log(JSON.stringify(data))
			error && error(err)
		}
		else {
			console.log(JSON.stringify(data))
			success && success(data)
		}
	});
}
// /**
//  * Query a sensor.
//  * @param sensorid ID of the sensor
//  * @param success Success callback: success(items)
//  *   (item fields: item.Timestamp, item.Value)
//  * @param error Error callback: success(err)
//  */
// evothings.aws.query = function (sensorid, success, error) {
// 	var params = {
// 		Payload: JSON.stringify({
// 			operation: 'query',
// 			sensorid: sensorid
// 		})
// 	}
// 	evothings.aws.ec2.invoke(
// 		params,
// 		function (err, data) {
// 			if (err) {
// 				error && error(err)
// 			}
// 			else {
// 				var items = JSON.parse(data.Payload).Items
// 				success && success(items)
// 			}
// 		}
// 	)
// }

/**
 * Query a sensor.
 * @param sensorid ID of the sensor
 * @param success Success callback: success(items)
 *   (item fields: item.Timestamp, item.Value)
 * @param error Error callback: success(err)
 */
evothings.aws.query = function (sensorid, success, error) {
	var params = {
		InstanceIds: [
			"i-056d98a0bc013fbbc"
		],
		AdditionalInfo: sensorid
	};
	evothings.aws.ec2.invoke(
		params,
		function (err, data) {
			if (err) {
				error && error(err)
			}
			else {
				var items = JSON.parse(data.Payload).Items
				success && success(items)
			}
		}
	)
}
