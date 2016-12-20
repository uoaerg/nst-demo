/* from wikipdia
DSCP value 	Hex value 	Decimal value 	Meaning 				
101 110 	0x2e 		46 				Expedited forwarding (EF)
000 000 	0x00 		0 				Best effort
001 010 	0x0a 		10 				AF11 	
001 100 	0x0c 		12 				AF12 
001 110 	0x0e 		14 				AF13
010 010 	0x12 		18 				AF21
010 100 	0x14 		20 				AF22
010 110 	0x16 		22 				AF23
011 010 	0x1a 		26 				AF31
011 100 	0x1c 		28 				AF32
011 110 	0x1e 		30 				AF33
100 010 	0x22 		34 				AF41
100 100 	0x24 		36 				AF42
100 110 	0x26 		38 				AF43
*/

var dscp_labels = [
	"EF",
	"BE",
	"AF11",
	"AF12",
	"AF13",
	"AF21",
	"AF22",
	"AF23",
	"AF31",
	"AF32",
	"AF33",
	"AF41",
	"AF42",
	"AF43",
	"Other"
]

var dscp_label_colours = [
	'#005151',
	'#7f3333',
	'#51cccc',
	'#337f7f',
	'#33467f',
	'#8ecc51',
	'#597f33',
	'#51cc70',
	'#8e51cc',
	'#59337f',
	'#5170cc',
	'#ccad51',
	'#7f6c33',
	'#cc6c33',
	'#cc51ad',
]

var dscp_map = [ true, true, true, true, true, true, true, true, true, true,
true, true, true, true, true ];

function setupcharts() 
{
	var charts = {}
	charts.eth1line = c3.generate({
		bindto: ".eth1-line",
		data: {
			columns: [
				['rx'].concat(new Array(100).fill(0)),
				['tx'].concat(new Array(100).fill(0)),
			]
		},
		point: {
			show: false
		},
		axis: {
			y: { show: false },
			x: { show: false }
		},
		legend: { hide: true },
		interaction: {enabled: false},
		transition: { duration: 0 },
	});

	charts.eth1rxgauge = c3.generate({
		bindto: ".eth1-rx-gauge",
		data: {
		columns: [
			['rx', 30],
		],
		type : 'gauge',
		},
		gauge: {
			label: {
				format: formatbandwidth,
				show: false 
			},
			max: 1000000, 
		},
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
				format: formatbandwidth,
				show: false 
			},
			max: 1000000, 
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
				['rx'].concat(new Array(100).fill(0)),
				['tx'].concat(new Array(100).fill(0)),
			]
		},
		point: {
			show: false
		},
		axis: {
			y: { show: false },
			x: { show: false }
		},
		legend: { hide: true },
		interaction: {enabled: false},
		transition: { duration: 0 },
	});

	charts.eth2rxgauge = c3.generate({
		bindto: ".eth2-rx-gauge",
		data: {
			columns: [
				['rx', 30],
			],
			type : 'gauge',
		},
		gauge: {
			label: {
				format: formatbandwidth,
				show: false 
			},
			max: 1000000, 
		},
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
		gauge: {
			label: {
				format: formatbandwidth,
				show: false 
			},
			max: 1000000, 
		},
		color: {
			pattern: ['#88CC88', '#55AA55', '#116611', '#004400'],
			threshold: {
				values: [30, 60, 90, 100]
			}
		}
	});

	charts.dscpbar = c3.generate({
		bindto: ".dscp-bar",
		data: {
			columns: [
				['DSCP Values', 35, 40, 10, 1, 4, 0, 0, 5, 0, 0, 0, 0, 0, 4,1]
			],
			type: 'bar',
			color: function (color, d) { return dscp_label_colours[d.index];},
			onclick: onbarchartclick
		},
		bar: {
			width: 50, // this makes bar width 100px
		},
		size: {
			height: 200,
			width: 1000
		},
		axis: {
			x: {
				type: 'category',
				categories: dscp_labels
			}
		},
		interaction: {enabled: true},
	});

	d3.selectAll('.tick').on('click', onbarchartclick);

	return charts;
}

function onbarchartclick(value, index)
{
	//console.dir(this);
	//console.dir([value, index]);
	console.log(dscp_labels[value]);

	dscp_map[value] = !dscp_map[value];
}

function formatbandwidth(bytes, ratio)	
{
	bits = bytes * 8

	if(bits > (1024 * 1024)) {
		return Math.floor(bits/ (1024*1024)) + ' Mb/s'
	} else if(bits > 1024) {
		return Math.floor(bits/ (1024)) + ' Kb/s'
	} 
	return Math.floor(bits) + ' b/s'
}

var ws;

function init()
{
	var charts = setupcharts();

	websocketuri= "ws://" + window.location.hostname + ":8080/ifstatus";

	ws = new WebSocket(websocketuri, "SUPERNET");

	ws.onopen = function (event) {
		console.log("ws connected");
	};

	ws.onmessage = function (event) {
		console.log(dscp_map)
		console.log(JSON.stringify(dscp_map));
		ws.send(JSON.stringify(dscp_map));

		netdata = JSON.parse(event.data);

		if(!netdata['interfaces'] ||!netdata['interfaces'].length)
			return;

		eth1 = netdata['interfaces'][1];
		eth2 = netdata['interfaces'][2];

		dscp = netdata['dscp'];

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
				['tx'].concat(netdata[eth1]["tx"].slice(-1)[0]),
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
				['tx'].concat(netdata[eth2]["tx"].slice(-1)[0]),
			]
		});

		charts.dscpbar.load({
			columns: [
				['DSCP Values'].concat(dscp)
			]
		});
	}
}
