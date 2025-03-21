document.addEventListener("DOMContentLoaded", () => {
    let totalSteps = 0;
    let leaderboard = [
      { name: "Alice", steps: 12000 },
      { name: "Bob", steps: 9500 },
      { name: "Charlie", steps: 8000 },
    ];
  
    const stepsInput = document.getElementById("stepsInput");
    const submitButton = document.getElementById("submitSteps");
    const leaderboardDiv = document.getElementById("leaderboard");
    const badgeMessage = document.getElementById("badgeMessage");
  
    function updateLeaderboard() {
      leaderboardDiv.innerHTML = "<h3>Top Step Achievers:</h3>";
      leaderboard.forEach((entry) => {
        const p = document.createElement("p");
        p.textContent = `${entry.name}: ${entry.steps} steps`;
        leaderboardDiv.appendChild(p);
      });
    }
  
    submitButton.addEventListener("click", () => {
      const steps = parseInt(stepsInput.value, 10);
      
      if (!steps || isNaN(steps) || steps <= 0) {
        alert("Please enter a valid step count.");
        return;
      }
  
      totalSteps += steps;
      stepsInput.value = "";
  
      let userIndex = leaderboard.findIndex((item) => item.name === "You");
  
      if (userIndex !== -1) {
        leaderboard[userIndex].steps += steps;
      } else {
        leaderboard.push({ name: "You", steps: steps });
      }
  
      leaderboard.sort((a, b) => b.steps - a.steps);
      updateLeaderboard();
  
      if (totalSteps >= 5000) {
        badgeMessage.innerHTML = "🏅 Congrats! You earned a badge!";
        badgeMessage.style.color = "green";
      } else {
        badgeMessage.innerHTML = `Keep going! Try to reach 5000 steps to earn a badge.`;
        badgeMessage.style.color = "black";
      }
    });
  
    updateLeaderboard();
  });
  