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

	charts.eth1rxgauge = c3.generate({
		bindto: ".eth1-rx-gauge",
		data: {
		columns: [
			['rx', 30],
		],
		type : 'gauge',
		},
		donut: {
			title: "ETH1 RATE"
		},
		legend: { hide: true },
		color: {
			pattern: [ '#7887AB', '#4F628E', '#162955', '#061539'],
			threshold: {
				values: [30, 60, 90, 100]
			}
		}
	});

	charts.eth1txgauge = c3.generate({
		bindto: ".eth1-tx-gauge",
		data: {
			columns: [
				['tx', 30],
			],
			type : 'gauge',
		},
		gauge: {
			label: {
				format: function(value, ratio) {
					return value + ' KB/s';
				},
				show: false 
			},
			max: 100000000, 
		},
		color: {
			pattern: ['#88CC88', '#55AA55', '#116611', '#004400'],
			threshold: {
				values: [30, 60, 90, 100]
			}
		}
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
	charts.eth2rxgauge = c3.generate({
		bindto: ".eth2-rx-gauge",
		data: {
		columns: [
			['rx', 30],
		],
		type : 'gauge',
		},
		donut: {
			title: "ETH1 RATE"
		},
		legend: { hide: true },
		color: {
			pattern: [ '#7887AB', '#4F628E', '#162955', '#061539'],
			threshold: {
				values: [30, 60, 90, 100]
			}
		}
	});

	charts.eth2txgauge = c3.generate({
		bindto: ".eth2-tx-gauge",
		data: {
		columns: [
			['tx', 30],
		],
		type : 'gauge',
		},
		donut: {
			title: "ETH1 RATE"
		},
		legend: { hide: true },
		color: {
			pattern: ['#88CC88', '#55AA55', '#116611', '#004400'],
			threshold: {
				values: [30, 60, 90, 100]
			}
		}
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

		if(!netdata['interfaces'] ||!netdata['interfaces'].length)
			return;

		eth1 = netdata['interfaces'][0]
		eth2 = netdata['interfaces'][1]

		charts.eth1line.load({
			columns: [
				['rx'].concat(netdata[eth1]["rx"]),
				['tx'].concat(netdata[eth1]["tx"])
			]
		});

		charts.eth1rxgauge .load({
			columns: [
				['rx'].concat(netdata[eth1]["rx"].slice(-1)[0]),
			]
		});

		charts.eth1txgauge .load({
			columns: [
				['tx'].concat(netdata[eth1]["rx"].slice(-1)[0]),
			]
		});

		charts.eth2line.load({
			columns: [
				['rx'].concat(netdata[eth2]["rx"]),
				['tx'].concat(netdata[eth2]["tx"])
			]
		});

		charts.eth2rxgauge .load({
			columns: [
				['rx'].concat(netdata[eth2]["rx"].slice(-1)[0]),
			]
		});

		charts.eth2txgauge .load({
			columns: [
				['tx'].concat(netdata[eth2]["rx"].slice(-1)[0]),
			]
		});
	}
}
