var diameter = require('./lib/diameter');


HOST = '0.0.0.0';
PORT = 3869;


var options = {
    beforeAnyMessage: diameter.logMessage,
    afterAnyMessage: diameter.logMessage,
};

var server = diameter.createServer(options, function(socket) {
    socket.on('diameterMessage', function(event) {
        console.log('Got message: ' + JSON.stringify(event.message));
        if (event.message.command === 'Capabilities-Exchange') {
            event.response.body = event.response.body.concat([
                    ['Result-Code', 'DIAMETER_SUCCESS'],  // Success response
                    ['Origin-Host', 'ocs.epc.mnc001.mcc001.3gppnetwork.org'],
                    ['Origin-Realm', 'epc.mnc001.mcc001.3gppnetwork.org'],
                    ['Host-IP-Address', '127.0.0.1'],  // IP address of this node
                    ['Vendor-Id', 10415],  // 3GPP Vendor ID (not 0)
                    ['Product-Name', 'node-diameter'],  // Software name
                    ['Firmware-Revision', 10201],  // Version info
                    ['Inband-Security-Id', 'NO_INBAND_SECURITY'],  // Security mode
                    ['Supported-Vendor-Id', 10415],  // Declares support for 3GPP
                    ['Auth-Application-Id', 'Diameter Credit Control Application'],  // Common Diameter support
                    ['Vendor-Specific-Application-Id', [
                        ['Vendor-Id', 10415],
                        ['Auth-Application-Id', 16777238]  // Gy (Online Charging)
                    ]]
            ]);
            event.callback(event.response);
        } else if (event.message.command === 'Credit-Control') {
            event.response.body = event.response.body.concat([
                ['Result-Code', 2001], // You can also define enum values by their integer codes
                [264, 'test.com'], // or AVP names, this is 'Origin-Host'
                ['Origin-Realm', 'epc.mnc001.mcc001.3gppnetwork.org'],
                ['Auth-Application-Id', 'Diameter Credit Control Application'],
                ['CC-Request-Type', 'INITIAL_REQUEST'],
                ['CC-Request-Number', 0],
                ['Multiple-Services-Credit-Control', [
                    ['Granted-Service-Unit', [
                        ['CC-Time', 123],
                        ['CC-Money', [
                            ['Unit-Value', [
                                ['Value-Digits', 123],
                                ['Exponent', 1]
                            ]],
                            ['Currency-Code', 1]
                        ]],
                        ['CC-Total-Octets', 123],
                        ['CC-Input-Octets', 123],
                        ['CC-Output-Octets', 123]
                    ]],
                    ['Requested-Service-Unit', [
                        ['CC-Time', 123],
                        ['CC-Money', [
                            ['Unit-Value', [
                                ['Value-Digits', 123],
                                ['Exponent', 1]
                            ]],
                            ['Currency-Code', 1]
                        ]],
                        ['CC-Total-Octets', 123],
                        ['CC-Input-Octets', 123],
                        ['CC-Output-Octets', 123]
                    ]]
                ]]
            ]);
            event.callback(event.response);
        }

        // Example server initiated message
        /*setTimeout(function() {
            console.log('Sending server initiated message');
            var connection = socket.diameterConnection;
            var request = connection.createRequest('Diameter Common Messages', 'Capabilities-Exchange');
    		request.body = request.body.concat([
    			[ 'Origin-Host', 'gx.pcef.com' ],
    			[ 'Origin-Realm', 'pcef.com' ],
    			[ 'Vendor-Id', 10415 ],
    			[ 'Origin-State-Id', 219081 ],
    			[ 'Supported-Vendor-Id', 10415 ],
    			[ 'Auth-Application-Id', 'Diameter Credit Control Application' ]
    		]);
    		connection.sendRequest(request).then(function(response) {
    			console.log('Got response for server initiated message');
    		}, function(error) {
    			console.log('Error sending request: ' + error);
    		});
        }, 2000); */
    });

    socket.on('end', function() {
        console.log('Client disconnected.');
    });
    socket.on('error', function(err) {
        console.log(err);
    });
});

server.listen(PORT, HOST);

console.log('Started DIAMETER server on ' + HOST + ':' + PORT);