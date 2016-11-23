function setupcharts() 
{
	var charts = {}
	charts.eth1line = c3.generate({
		bindto: ".eth1-line",
		data: {
			columns: [
				['rx', 30, 200, 100, 400, 150, 250],
				['tx', 50, 20, 10, 40, 15, 25]
			]
		},
		axis: {
			y: { show: false },
			x: { show: false }
		},
		legend: { hide: true },
	});

	charts.eth1donut = c3.generate({
		bindto: ".eth1-donut",
		data: {
		columns: [
			['rx', 30],
			['tx', 120],
		],
		type : 'donut',
		},
		donut: {
			title: "ETH1 RATE"
		},
		legend: { hide: true },
	});

	charts.eth2line = c3.generate({
		bindto: ".eth2-line",
		data: {
			columns: [
				['rx', 30, 200, 100, 400, 150, 250],
				['tx', 50, 20, 10, 40, 15, 25]
			]
		},
		axis: {
			y: { show: false },
			x: { show: false }
		},
		legend: { hide: true },
	});

	charts.eth2donut = c3.generate({
		bindto: ".eth2-donut",
		data: {
		columns: [
			['rx', 30],
			['tx', 120],
		],
		type : 'donut',
		},
		donut: {
			title: "ETH2 RATE"
		},
		legend: { hide: true },
	});

	return charts;
}

var ws;

function init()
{
	console.log("init call");
	var charts = setupcharts();
	console.log(charts);

	ws = new WebSocket("ws://localhost:8080/ifstatus", "SUPERNET");
	ws.onopen = function (event) {
		console.log("ws connected");
	};

	ws.onmessage = function (event) {
		netdata = JSON.parse(event.data)

		charts.eth1line.load({
			columns: [
				['rx'].concat(netdata["eth1"]["rx"]),
				['tx'].concat(netdata["eth1"]["tx"])
			]
		});
		charts.eth1donut.load({
			columns: [
				['rx'].concat(netdata["eth1"]["rx"].slice(-1)[0]),
				['tx'].concat(netdata["eth1"]["tx"].slice(-1)[0])
			]
		});

		charts.eth2line.load({
			columns: [
				['rx'].concat(netdata["eth2"]["rx"]),
				['tx'].concat(netdata["eth2"]["tx"])
			]
		});
		charts.eth2donut.load({
			columns: [
				['rx'].concat(netdata["eth2"]["rx"].slice(-1)[0] ),
				['tx'].concat(netdata["eth2"]["tx"].slice(-1)[0] )
			]
		});
	}
}
