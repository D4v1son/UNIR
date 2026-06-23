for j=1, #KEYS do
    redis.call('hmset', 'userA' .. j, 'name', KEYS[j], 'age', ARGV[j])
end