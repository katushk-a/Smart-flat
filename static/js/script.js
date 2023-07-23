const lightOnBtn2 = document.getElementById("light-on2");
const lightOffBtn2 = document.getElementById("light-off2");
const lightOnBtn1 = document.getElementById("light-on");
const lightOffBtn1 = document.getElementById("light-off");
const brightnessSlider3 = document.getElementById("brightness-slider");
const tempReading = document.getElementById("temp-reading");
const lightStatus1 = document.getElementById("light-status");
const lightStatus2 = document.getElementById("light-status2");
const brightnessStatus3 = document.getElementById("brightness-value");

const lightbulb1 = document.getElementById("light1");
const lightbulb2 = document.getElementById("light2");
const lightbulb3 = document.getElementById("light3");

lightStatus1.textContent = "Off";
lightStatus2.textContent = "Off";
brightnessStatus3.textContent = 50;
tempReading.textContent = (Math.random() * (31 - 9) + 9).toFixed(1).toString() + '°C';
n1 = 24.5;
n2 = 25.1;
heating = false;
ms = 1500;


lightOnBtn1.addEventListener("click", () => {
  fetch("/light-on")
    .then(response => response.json())
    .then(text => {
      lightStatus1.textContent = text.light1 ? "On" : "Off";
      lightbulb1.style.opacity = text.light1 ? '1' : '0';
      console.log(text.message);
    })
    .catch(error => console.error(error));
});

lightOffBtn1.addEventListener("click", () => {
  fetch("/light-off")
    .then(response => response.json())
    .then(text => {
      lightStatus1.textContent = text.light1 ? "On" : "Off";
      lightbulb1.style.opacity = text.light1 ? '1' : '0';
      console.log(text.message);
    })
    .catch(error => console.error(error));
});

lightOnBtn2.addEventListener("click", () => {
  fetch("/light-on2")
    .then(response => response.json())
    .then(text => {
      lightStatus2.textContent = text.light2 ? "On" : "Off";
      lightbulb2.style.opacity = text.light2 ? '1' : '0';
      console.log(text.message);
    })
    .catch(error => console.error(error));
});

lightOffBtn2.addEventListener("click", () => {
  fetch("/light-off2")
    .then(response => response.json())
    .then(text => {
      lightStatus2.textContent = text.light2 ? "On" : "Off";
      lightbulb2.style.opacity = text.light2 ? '1' : '0';
      console.log(text.message);
    })
    .catch(error => console.error(error));
});

brightnessSlider3.addEventListener("input", () => {
  const brightness = brightnessSlider3.value;
  fetch(`/brightness-control3?brightness3=${brightness}`)
    .then(response => response.json())
    .then(text => {
      brightnessStatus3.textContent = text.brightness;
      lightbulb3.style.opacity = (text.brightness / 100).toString()
      console.log(text.message);
    })
    .catch(error => console.error(error));
});



const temperatureChart = new Chart(document.getElementById("temperature-chart1"), {
  type: "line",
  data: {
    labels: [],
    datasets: [
      {
        label: "Temperature",
        data: [],
        fill: false,
        borderColor: "rgb(75, 192, 192)",
        tension: 0.1
      }
    ]
  },
  options: {
    scales: {
      x: {
        display: false
      }
    }
  }
});

const updateThresholdsBtn = document.getElementById("update-thresholds-btn");
const lowerThresholdInput = document.getElementById("lower-threshold");
lowerThresholdInput.value = n1;
const upperThresholdInput = document.getElementById("upper-threshold");
upperThresholdInput.value = n2;
const heatingSystemStatus = document.getElementById("heating-system-status");
heatingSystemStatus.innerText = heating;

updateThresholdsBtn.addEventListener("click", () => {
        const lowerThreshold = parseInt(lowerThresholdInput.value);
        const upperThreshold = parseInt(upperThresholdInput.value);

        fetch("/update-thresholds", {
          method: "POST",
          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
          },
          body: `lower_threshold=${lowerThreshold}&upper_threshold=${upperThreshold}`,
        })
          .then((response) => response.json())
          .then((data) => {
            heatingSystemStatus.textContent = data.status;
            console.log(data.message);
          })
          .catch((error) => console.error(error));
  });


setInterval(() => {
  fetch("/get-temp-reading")
    .then(response => response.json())
    .then(data => {
      const currentTimestamp = new Date().toLocaleTimeString();
      temperatureChart.data.labels.push(currentTimestamp);
      temperatureChart.data.datasets[0].data.push(data.temp_reading);
      temperatureChart.update();
      if (temperatureChart.data.labels.length > 20) {
        temperatureChart.data.labels.shift();
        temperatureChart.data.datasets[0].data.shift();
      }
      tempReading.textContent = `${data.temp_reading} °C`;
      heatingSystemStatus.textContent = data.heating_system;
      console.log(`Temperature in the apartment has changed to ${data.temp_reading} °C`);
    })
    .catch(error => console.error(error));
}, ms);
