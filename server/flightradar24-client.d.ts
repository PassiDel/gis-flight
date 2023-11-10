declare module 'flightradar24-client' {
  function fetchFlight(flight: any): Promise<{
    id: any;
    callsign: any;
    liveData: any;
    model: any;
    registration: any;
    airline: any;
    origin: {
      id: any;
      name: any;
      coordinates: {
        latitude: any;
        longitude: any;
        altitude: any;
      };
      timezone: any;
      country: any;
    };
    destination: {
      id: any;
      name: any;
      coordinates: {
        latitude: any;
        longitude: any;
        altitude: any;
      };
      timezone: any;
      country: any;
    };
    departure: any;
    scheduledDeparture: any;
    departureTerminal: any;
    departureGate: any;
    arrival: any;
    scheduledArrival: any;
    arrivalTerminal: any;
    arrivalGate: any;
    delay: any;
  }>;
  function fetchFromRadar(
    north: number,
    west: number,
    south: number,
    east: number,
    when?: number,
    opt?: Partial<{
      FAA: boolean;
      FLARM: boolean;
      MLAT: boolean;
      ADSB: boolean;
      inAir: boolean;
      onGround: boolean;
      inactive: boolean;
      gliders: boolean;
      estimatedPositions: boolean;
    }>
  ): Promise<
    {
      id: string;
      registration: string;
      flight: string;
      callsign: string;
      origin: string;
      destination: string;
      latitude: number;
      longitude: number;
      altitude: number;
      bearing: number;
      speed: number;
      rateOfClimb: number;
      isOnGround: boolean;
      squawkCode: string;
      model: string;
      modeSCode: string;
      radar: string;
      isGlider: boolean;
      timestamp: number;
    }[]
  >;
}
