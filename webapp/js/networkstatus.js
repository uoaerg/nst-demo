var eth1line = c3.generate({
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

var eth1donut = c3.generate({
	bindto: ".eth1-donut",
	data: {
	columns: [
		['data1', 30],
		['data2', 120],
	],
	type : 'donut',
	},
	donut: {
		title: "ETH1 RATE"
	},
	legend: { hide: true },
});

var eth2line = c3.generate({
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

var eth2donut = c3.generate({
	bindto: ".eth2-donut",
	data: {
	columns: [
		['data1', 30],
		['data2', 120],
	],
	type : 'donut',
	},
	donut: {
		title: "ETH2 RATE"
	},
	legend: { hide: true },
});
