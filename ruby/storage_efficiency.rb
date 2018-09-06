require '../../pmemkv-ruby/lib/pmemkv/kv_engine'

PATH = '/dev/shm/pmemkv'

def test_engine(engine, size, value)
  puts "\nTesting #{engine} engine: size=#{size}, value.length=#{value.length}"

  File.delete(PATH) if File.exist?(PATH)
  kv = KVEngine.new(engine, PATH, size)
  last_key = 0
  total_chars = 0
  begin
    100000000.times do |i|
      istr = i.to_s
      kv.put(istr, value)
      last_key = i
      total_chars += (istr.length + value.length)
    end
    expect(true).to be false
  rescue RuntimeError => e
    puts "   keys = #{last_key}"
    puts "   efficiency = #{total_chars / size.to_f}"
  end
  kv.close

end

test_engine('btree', 64 * 1024 * 1024, '')
test_engine('btree', 1024 * 1024 * 1024, '')
test_engine('btree', 64 * 1024 * 1024, 'A' * 16)
test_engine('btree', 1024 * 1024 * 1024, 'A' * 16)
test_engine('btree', 64 * 1024 * 1024, 'A' * 64)
test_engine('btree', 1024 * 1024 * 1024, 'A' * 64)
test_engine('btree', 64 * 1024 * 1024, 'A' * 128)
test_engine('btree', 1024 * 1024 * 1024, 'A' * 128)

test_engine('kvtree3', 64 * 1024 * 1024, '')
test_engine('kvtree3', 1024 * 1024 * 1024, '')
test_engine('kvtree3', 64 * 1024 * 1024, 'A' * 16)
test_engine('kvtree3', 1024 * 1024 * 1024, 'A' * 16)
test_engine('kvtree3', 64 * 1024 * 1024, 'A' * 64)
test_engine('kvtree3', 1024 * 1024 * 1024, 'A' * 64)
test_engine('kvtree3', 64 * 1024 * 1024, 'A' * 128)
test_engine('kvtree3', 1024 * 1024 * 1024, 'A' * 128)
test_engine('kvtree3', 64 * 1024 * 1024, 'A' * 256)
test_engine('kvtree3', 1024 * 1024 * 1024, 'A' * 256)
test_engine('kvtree3', 64 * 1024 * 1024, 'A' * 512)
test_engine('kvtree3', 1024 * 1024 * 1024, 'A' * 512)
test_engine('kvtree3', 64 * 1024 * 1024, 'A' * 2048)
test_engine('kvtree3', 1024 * 1024 * 1024, 'A' * 2048)
test_engine('kvtree3', 2 * 1024 * 1024 * 1024, 'A' * 2048)

puts "\nFinished!\n\n"
