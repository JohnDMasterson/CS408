import unittest
import iclicker

base = iclicker.iClickerBaseMock()

# init_base tests
print "init_base:"

base.init_base()
assert(base.frequency == [0, 0])

print "PASS\n"


# set_frequency tests
print "set_frequency:"

base.set_frequency('A', 'A')
assert(base.frequency == [0, 0])

base.set_frequency('A', 'B')
assert(base.frequency == [0, 1])

base.set_frequency('b', 'A')
assert(base.frequency == [1, 0])

base.set_frequency('C', 'c')
assert(base.frequency == [2, 2])

base.set_frequency('D', 'd')
assert(base.frequency == [3, 3])

print "PASS\n"


# set_poll_type tests
print "set_poll_type:"

base.set_poll_type()
assert(base.poll_type == 0)

base.set_poll_type('alpha')
assert(base.poll_type == 0)

base.set_poll_type('numeric')
assert(base.poll_type == 1)

base.set_poll_type('alphanumeric')
assert(base.poll_type == 2)

print "PASS\n"


# polling
print "polling:"

# stopping a non-existent poll
error = False
try:
    base.stop_poll()
except ValueError as e:
    error = True
assert(error == True)

# default poll success
error = False
try:
    base.start_poll()
    assert(base.poll_type == 0)
    base.stop_poll()
except ValueError as e:
    error = True
assert(error == False)

# alphanumeric poll success
error = False
try:
    base.start_poll('alphanumeric')
    assert(base.poll_type == 2)
    base.stop_poll()
except ValueError as e:
    error = True
assert(error == False)

# starting a poll twice
error = False
try:
    base.start_poll()
    base.start_poll()
except ValueError as e:
    error = True
assert(error == True)

# stopping a poll twice
error = False
try:
    base.start_poll()
    base.stop_poll()
    base.stop_poll()
except ValueError as e:
    error = True
assert(error == True)


print "PASS\n"
