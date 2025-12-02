"""Test that market data is now dynamic (not static)."""

from modules.market_data import MarketDataGenerator

# Test 1: Random seeds produce different results
print("\n" + "="*70)
print("TEST: Market Data is Dynamic (Not Static)")
print("="*70)

gen1 = MarketDataGenerator(seed=None)
s1 = gen1.generate_scenario()

gen2 = MarketDataGenerator(seed=None)
s2 = gen2.generate_scenario()

print(f"\nScenario 1 first price: £{s1.price_gbp_kwh[0]:.4f}/kWh")
print(f"Scenario 2 first price: £{s2.price_gbp_kwh[0]:.4f}/kWh")

if s1.price_gbp_kwh[0] != s2.price_gbp_kwh[0]:
    print("\n[PASS] Market is dynamic - prices change between runs")
else:
    print("\n[FAIL] Market is static - prices are the same")

# Test 2: Fixed seed still works for testing
print("\n" + "="*70)
print("TEST: Fixed Seed Still Works (Reproducibility)")
print("="*70)

gen3 = MarketDataGenerator(seed=42)
s3 = gen3.generate_scenario()

gen4 = MarketDataGenerator(seed=42)
s4 = gen4.generate_scenario()

print(f"\nScenario 3 (seed=42): £{s3.price_gbp_kwh[0]:.4f}/kWh")
print(f"Scenario 4 (seed=42): £{s4.price_gbp_kwh[0]:.4f}/kWh")

if s3.price_gbp_kwh[0] == s4.price_gbp_kwh[0]:
    print("\n[PASS] Fixed seed produces reproducible results")
else:
    print("\n[FAIL] Fixed seed doesn't match")

print("\n" + "="*70)
print("TEST COMPLETE")
print("="*70 + "\n")
