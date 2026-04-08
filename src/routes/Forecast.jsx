import NextDayForecastCard from "../components/widgets/NextDayForecastCard";
import SeasonalRiskInsightsCard from "../components/widgets/SeasonalRiskInsightsCard";

function SevenDay() {
  return (
    <>
      <div className="grid grid-cols-1 gap-6">
        <NextDayForecastCard />
        <SeasonalRiskInsightsCard />
      </div>
    </>
  );
}

export default SevenDay;
