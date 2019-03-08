require '../../pmemkv-ruby/lib/pmemkv/kv_engine'

PERSIST_PATH = '/dev/shm/pmemkv'
VOLATILE_PATH = '/dev/shm'

def test_engine(engine, path, size, value)
  puts "\nTesting #{engine} engine: size=#{size}, value.length=#{value.length}"

  File.delete(path) if path.equal?(PERSIST_PATH) && File.exist?(path)
  kv = KVEngine.new(engine, "{\"path\":\"#{path}\",\"size\":#{size}}")
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
  kv.stop

end

test_engine('tree3', PERSIST_PATH, 64 * 1024 * 1024, '')
test_engine('tree3', PERSIST_PATH, 1024 * 1024 * 1024, '')
test_engine('tree3', PERSIST_PATH, 64 * 1024 * 1024, 'A' * 16)
test_engine('tree3', PERSIST_PATH, 1024 * 1024 * 1024, 'A' * 16)
test_engine('tree3', PERSIST_PATH, 64 * 1024 * 1024, 'A' * 64)
test_engine('tree3', PERSIST_PATH, 1024 * 1024 * 1024, 'A' * 64)
test_engine('tree3', PERSIST_PATH, 64 * 1024 * 1024, 'A' * 128)
test_engine('tree3', PERSIST_PATH, 1024 * 1024 * 1024, 'A' * 128)
test_engine('tree3', PERSIST_PATH, 64 * 1024 * 1024, 'A' * 256)
test_engine('tree3', PERSIST_PATH, 1024 * 1024 * 1024, 'A' * 256)
test_engine('tree3', PERSIST_PATH, 64 * 1024 * 1024, 'A' * 512)
test_engine('tree3', PERSIST_PATH, 1024 * 1024 * 1024, 'A' * 512)
test_engine('tree3', PERSIST_PATH, 64 * 1024 * 1024, 'A' * 2048)
test_engine('tree3', PERSIST_PATH, 1024 * 1024 * 1024, 'A' * 2048)
test_engine('tree3', PERSIST_PATH, 2 * 1024 * 1024 * 1024, 'A' * 2048)

test_engine('vsmap', VOLATILE_PATH, 64 * 1024 * 1024, '')
test_engine('vsmap', VOLATILE_PATH, 1024 * 1024 * 1024, '')
test_engine('vsmap', VOLATILE_PATH, 64 * 1024 * 1024, 'A' * 16)
test_engine('vsmap', VOLATILE_PATH, 1024 * 1024 * 1024, 'A' * 16)
test_engine('vsmap', VOLATILE_PATH, 64 * 1024 * 1024, 'A' * 64)
test_engine('vsmap', VOLATILE_PATH, 1024 * 1024 * 1024, 'A' * 64)
test_engine('vsmap', VOLATILE_PATH, 64 * 1024 * 1024, 'A' * 128)
test_engine('vsmap', VOLATILE_PATH, 1024 * 1024 * 1024, 'A' * 128)
test_engine('vsmap', VOLATILE_PATH, 64 * 1024 * 1024, 'A' * 256)
test_engine('vsmap', VOLATILE_PATH, 1024 * 1024 * 1024, 'A' * 256)
test_engine('vsmap', VOLATILE_PATH, 64 * 1024 * 1024, 'A' * 512)
test_engine('vsmap', VOLATILE_PATH, 1024 * 1024 * 1024, 'A' * 512)
test_engine('vsmap', VOLATILE_PATH, 64 * 1024 * 1024, 'A' * 2048)
test_engine('vsmap', VOLATILE_PATH, 1024 * 1024 * 1024, 'A' * 2048)
test_engine('vsmap', VOLATILE_PATH, 2 * 1024 * 1024 * 1024, 'A' * 2048)

test_engine('vcmap', VOLATILE_PATH, 64 * 1024 * 1024, '')
test_engine('vcmap', VOLATILE_PATH, 1024 * 1024 * 1024, '')
test_engine('vcmap', VOLATILE_PATH, 64 * 1024 * 1024, 'A' * 16)
test_engine('vcmap', VOLATILE_PATH, 1024 * 1024 * 1024, 'A' * 16)
test_engine('vcmap', VOLATILE_PATH, 64 * 1024 * 1024, 'A' * 64)
test_engine('vcmap', VOLATILE_PATH, 1024 * 1024 * 1024, 'A' * 64)
test_engine('vcmap', VOLATILE_PATH, 64 * 1024 * 1024, 'A' * 128)
test_engine('vcmap', VOLATILE_PATH, 1024 * 1024 * 1024, 'A' * 128)
test_engine('vcmap', VOLATILE_PATH, 64 * 1024 * 1024, 'A' * 256)
test_engine('vcmap', VOLATILE_PATH, 1024 * 1024 * 1024, 'A' * 256)
test_engine('vcmap', VOLATILE_PATH, 64 * 1024 * 1024, 'A' * 512)
test_engine('vcmap', VOLATILE_PATH, 1024 * 1024 * 1024, 'A' * 512)
test_engine('vcmap', VOLATILE_PATH, 64 * 1024 * 1024, 'A' * 2048)
test_engine('vcmap', VOLATILE_PATH, 1024 * 1024 * 1024, 'A' * 2048)
test_engine('vcmap', VOLATILE_PATH, 2 * 1024 * 1024 * 1024, 'A' * 2048)

puts "\nFinished!\n\n"
