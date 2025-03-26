"use client";

import ContactButton from "@/components/ContactButton";
import ProfileMenu from "@/components/ProfileMenu";
import {
  Grid,
  GridItem,
  Flex,
  Box,
  Button,
  CloseButton,
  Menu,
  Portal,
  Dialog,
  Field,
  Stack,
  Input,
} from "@chakra-ui/react";
import { useRef } from "react";
import { CgFile, CgLogOut, CgUserAdd } from "react-icons/cg";

export default function App() {
  const refAvatar = useRef<HTMLInputElement>(null);
  const refContact = useRef<HTMLInputElement>(null);
  return (
    <Grid templateColumns="0.5fr 4fr" height="100vh">
      <GridItem borderWidth="2px" borderColor="gray.700" p="1px">
        <Flex
          direction="column"
          height="100%"
          borderRight="1px"
          borderColor="gray.500"
        >
          <ContactButton
            avatar="https://i.pravatar.cc/301"
            number={123123123}
            ID="XD"
          />
          <ContactButton
            avatar="https://i.pravatar.cc/310"
            number={123123123}
            ID="XD"
          />
          <ContactButton
            avatar="https://i.pravatar.cc/320"
            number={123123123}
            ID="XD"
          />
          <Box marginTop="auto">
            <Menu.Root>
              <Menu.Trigger asChild>
                <Button
                  height="fit-content"
                  bg="blue.400"
                  margin="0.5vh 0 0 0"
                  cursor="pointer"
                >
                  <ProfileMenu
                    avatar="https://i.pravatar.cc/300"
                    number={123123123}
                  />
                </Button>
              </Menu.Trigger>
              <Portal>
                <Menu.Positioner>
                  <Menu.Content>
                    <Flex direction="column">
                      <Dialog.Root initialFocusEl={() => refContact.current}>
                        <Dialog.Trigger asChild>
                          <Button
                            variant="outline"
                            width="10vw"
                            margin="0 0 1vh 0"
                          >
                            <CgUserAdd />
                            <Box flex="1">Add contact</Box>
                          </Button>
                        </Dialog.Trigger>
                        <Portal>
                          <Dialog.Backdrop />
                          <Dialog.Positioner>
                            <Dialog.Content>
                              <Dialog.Header>
                                <Dialog.Title>Add contact</Dialog.Title>
                              </Dialog.Header>
                              <Dialog.Body pb="4">
                                <Stack gap="4">
                                  <Field.Root>
                                    <Field.Label>Contact number</Field.Label>
                                    <Input
                                      name="addNumber"
                                      type="number"
                                      ref={refContact}
                                      placeholder="123123123"
                                    />
                                  </Field.Root>
                                </Stack>
                              </Dialog.Body>
                              <Dialog.Footer>
                                <Dialog.ActionTrigger asChild>
                                  <Button variant="outline">Cancel</Button>
                                </Dialog.ActionTrigger>
                                <Button colorPalette="green">Add</Button>
                              </Dialog.Footer>
                            </Dialog.Content>
                          </Dialog.Positioner>
                        </Portal>
                      </Dialog.Root>
                      <Dialog.Root initialFocusEl={() => refAvatar.current}>
                        <Dialog.Trigger asChild>
                          <Button
                            variant="outline"
                            width="10vw"
                            margin="0 0 1vh 0"
                          >
                            <CgFile />
                            <Box flex="1">Change avatar</Box>
                          </Button>
                        </Dialog.Trigger>
                        <Portal>
                          <Dialog.Backdrop />
                          <Dialog.Positioner>
                            <Dialog.Content>
                              <Dialog.Header>
                                <Dialog.Title>Change avatar</Dialog.Title>
                              </Dialog.Header>
                              <Dialog.Body pb="4">
                                <Stack gap="4">
                                  <Field.Root>
                                    <Field.Label>Avatar URL</Field.Label>
                                    <Input
                                      ref={refAvatar}
                                      placeholder="https://i.pravatar.cc/150?u=fake@pravatar.com"
                                    />
                                  </Field.Root>
                                </Stack>
                              </Dialog.Body>
                              <Dialog.Footer>
                                <Dialog.ActionTrigger asChild>
                                  <Button variant="outline">Cancel</Button>
                                </Dialog.ActionTrigger>
                                <Button>Save</Button>
                              </Dialog.Footer>
                            </Dialog.Content>
                          </Dialog.Positioner>
                        </Portal>
                      </Dialog.Root>
                      <Dialog.Root role="alertdialog">
                        <Dialog.Trigger asChild>
                          <Button
                            variant="outline"
                            width="10vw"
                            colorPalette="red"
                          >
                            <CgLogOut />
                            <Box flex="1">Sign out</Box>
                          </Button>
                        </Dialog.Trigger>
                        <Portal>
                          <Dialog.Backdrop />
                          <Dialog.Positioner>
                            <Dialog.Content>
                              <Dialog.Header>
                                <Dialog.Title>Are you sure?</Dialog.Title>
                              </Dialog.Header>
                              <Dialog.Body>
                                <p>
                                  You'll be forwarded to the logging page.
                                  Wel'll miss you!
                                </p>
                              </Dialog.Body>
                              <Dialog.Footer>
                                <Dialog.ActionTrigger asChild>
                                  <Button variant="outline">
                                    Nevermind, take me back
                                  </Button>
                                </Dialog.ActionTrigger>
                                <Button colorPalette="red">I'm leaving</Button>
                              </Dialog.Footer>
                              <Dialog.CloseTrigger asChild>
                                <CloseButton size="sm" />
                              </Dialog.CloseTrigger>
                            </Dialog.Content>
                          </Dialog.Positioner>
                        </Portal>
                      </Dialog.Root>
                    </Flex>
                  </Menu.Content>
                </Menu.Positioner>
              </Portal>
            </Menu.Root>
          </Box>
        </Flex>
      </GridItem>
      <GridItem>
        <p>Hey</p>
      </GridItem>
    </Grid>
  );
}
